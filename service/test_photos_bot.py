from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import AsyncMock, MagicMock, patch

import PhotosBot


class PhotosBotStateTest(IsolatedAsyncioTestCase):
    def setUp(self):
        PhotosBot.active_service.clear()
        PhotosBot.waiting_for_summary.clear()

    async def test_set_service_stores_service_id_org_slug_and_folder(self):
        reply_text = AsyncMock()
        update = SimpleNamespace(
            callback_query=SimpleNamespace(
                message=SimpleNamespace(chat_id=321, reply_text=reply_text)
            )
        )
        service = {
            "id": 77,
            "service_number": 5,
            "created_at": "2026-04-28T12:00:00Z",
            "client": {"first_name": "Cliente Demo"},
            "employee": {"organization_slug": "org-a"},
        }

        with patch("PhotosBot.verify_or_create_ftp_folder") as verify_folder:
            await PhotosBot.set_service(update, SimpleNamespace(), service)

        self.assertEqual(
            PhotosBot.active_service[321],
            {
                "service_id": 77,
                "service_number": 5,
                "org_slug": "org-a",
                "folder": "5-Cliente Demo-2026-04-28",
            },
        )
        verify_folder.assert_called_once_with("org-a", "5-Cliente Demo-2026-04-28")
        reply_text.assert_awaited()

    async def test_handle_summary_fetches_service_by_service_id_not_service_number(self):
        chat_id = 321
        PhotosBot.active_service[chat_id] = {
            "service_id": 77,
            "service_number": 5,
            "org_slug": "org-a",
            "folder": "5-Cliente Demo-2026-04-28",
        }
        PhotosBot.waiting_for_summary[chat_id] = {
            "service_id": 77,
            "service_number": 5,
            "folder_name": "5-Cliente Demo-2026-04-28",
        }
        reply_text = AsyncMock()
        update = SimpleNamespace(
            message=SimpleNamespace(
                chat_id=chat_id,
                text="Trabajo terminado",
                reply_text=reply_text,
            )
        )

        get_response = MagicMock()
        get_response.raise_for_status.return_value = None
        get_response.json.return_value = {"id": 77, "service_number": 5}

        patch_response = MagicMock()
        patch_response.raise_for_status.return_value = None
        patch_response.json.return_value = {
            "id": 77,
            "service_number": 5,
            "client": {"first_name": "Cliente Demo"},
            "employee": {"first_name": "Ana"},
            "description": "desc",
            "status_name": "Finalizado",
        }

        with (
            patch("PhotosBot.requests.get", return_value=get_response) as mock_get,
            patch("PhotosBot.requests.patch", return_value=patch_response) as mock_patch,
            patch("PhotosBot.send_confirm_msg", new=AsyncMock()) as send_confirm,
        ):
            await PhotosBot.handle_summary(update, SimpleNamespace())

        mock_get.assert_called_once_with(f"{PhotosBot.API_URL}/service/77")
        mock_patch.assert_called_once()
        self.assertNotIn(chat_id, PhotosBot.active_service)
        self.assertNotIn(chat_id, PhotosBot.waiting_for_summary)
        send_confirm.assert_awaited_once()
        reply_text.assert_awaited_once()


class PhotosBotFtpHelpersTest(TestCase):
    def test_upload_a_ftp_uses_org_slug_prefix(self):
        ftp = MagicMock()

        with (
            patch("PhotosBot.connect_ftp", return_value=ftp),
            patch("builtins.open", MagicMock()),
        ):
            PhotosBot.upload_a_ftp("/tmp/demo.jpg", "org-a", "5-demo-2026-04-28", "demo.jpg")

        ftp.cwd.assert_called_once_with(f"{PhotosBot.FTP_PATH}/org-a/5-demo-2026-04-28")

    def test_verify_or_create_ftp_folder_creates_org_folder_before_service_folder(self):
        ftp = MagicMock()
        ftp.cwd.side_effect = [Exception("base missing"), None, Exception("service missing")]

        with patch("PhotosBot.connect_ftp", return_value=ftp):
            with patch("PhotosBot.ftplib.error_perm", Exception):
                PhotosBot.verify_or_create_ftp_folder("org-a", "5-demo-2026-04-28")

        ftp.mkd.assert_any_call(f"{PhotosBot.FTP_PATH}/org-a")
        ftp.mkd.assert_any_call("5-demo-2026-04-28")
