from aiohttp import web

from tg_notificator.appw import AppWrapper


class BaseView(web.View):
    def __init__(self, request):
        super().__init__(request)
        self.app_w = AppWrapper(request.app)


class NotifyView(BaseView):
    async def post(self):
        data = await self.request.json()

        target = data["target"]
        message = data["message"]

        tg_user = await self.app_w.user_registry.get_user_by_username(target)

        if not tg_user:
            return web.json_response(data={
                "description": f"No user '{target}' found in internal database"
            }, status=404)

        await self.app_w.bot.private(tg_user.private_chat_id).send_text(message)

        return web.Response(status=204)


class ListUserView(BaseView):
    async def get(self):
        all_users = await self.app_w.user_registry.list_users()

        return web.json_response(data=[
            user.dict()
            for user in all_users
        ])
