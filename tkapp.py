import tkinter as tk
import asyncio
import websockets
import json
import threading

class OrderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chef Orders")
        self.order_list = tk.Listbox(self.root, width=50, height=20)
        self.order_list.pack(pady=20)

        # Start the WebSocket listener in a separate thread
        threading.Thread(target=self.start_websocket, daemon=True).start()

    async def listen_orders(self):
        uri = "ws://localhost:8000/ws/orders/"
        async with websockets.connect(uri) as websocket:
            while True:
                message = await websocket.recv()
                order_data = json.loads(message)
                self.order_list.insert(tk.END, order_data['message'])

    def start_websocket(self):
        asyncio.run(self.listen_orders())

if __name__ == "__main__":
    root = tk.Tk()
    app = OrderApp(root)
    root.mainloop()
