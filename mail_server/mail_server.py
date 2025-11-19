from http.server import HTTPServer, BaseHTTPRequestHandler 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.header import Header
from email import encoders
import json
from config import SENDER_EMAIL, SENDER_PASSWORD, SMPT_PORT, SMPT_SERVER, PDF_PATH, LOGS_PATH
import os

class MailHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        print('GET')

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # Для CORS
        self.end_headers()

        # Отправляем ответ
        response = {
            "status": "success",
            "message": "GET request handled successfully",
            "path": self.path
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))


    def do_POST(self):
        print('POST')

        print('self.path', '|' + self.path + '|')
        # Проверяю путь
        if self.path != '/api/send-resume' or self.path != '/api/send-resume':
            self.send_error(404, "Endpoint not found")
            self.write_logs('Кто-то пытался отправить запрос по неверному пути')
            return            


        content_length = int(self.headers['Content-Length']) # Получаю длину тела запроса в байтах
        post_data = self.rfile.read(content_length).decode('utf-8') # Читаю нужное кол-во байтов и декодирую в строку 'utf-8'

        data = json.loads(post_data)
        send_to = data.get('to', '')

        if not send_to:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "error",
                "message": 'Mail is empty! It is wrong!'
            }

            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

            self.write_logs(f'Письмо не отправлено, не указали почту', send_to)
            return

        try:
            server = smtplib.SMTP(SMPT_SERVER, SMPT_PORT)
            server.starttls() # Включает шифрование соединения (Transport Layer Security), Защищает данные от перехвата
            server.login(SENDER_EMAIL, SENDER_PASSWORD) # Авторизуюсь на почтовом сервере

            # Для сообщений без вложений
            # message = MIMEText('Привет! Это тестовое сообщение.', 'plain', 'utf-8')

            # Для сообщений с вложениями
            message = MIMEMultipart()
            message.attach(MIMEText('Привет!\nPDF файл во вложении)', 'plain', 'utf-8'))

            message['Subject'] = Header("Резюме Тесовец Николай", 'utf-8')    # Тема
            message['From'] = "Николай Тесовец"   # Описание от кого
            message['To'] = send_to      # Описание получателя

            # Прикрепляю PDF файл
            if os.path.exists(PDF_PATH):

                with open(PDF_PATH, 'rb') as file:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(file.read())

                # Кодирует payload в base64 и добавляет заголовок
                encoders.encode_base64(part)

                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {os.path.basename(PDF_PATH)}",
                )

                message.attach(part)
                print('PDF файл прикреплен')
            else:
                print('PDF файл не найден')

            message.attach(MIMEText('\nЖду обратную связь 😉\n', 'plain', 'utf-8'))

            server.sendmail(SENDER_EMAIL, send_to, message.as_string()) # Отправляю сообщение .as_string() ВАЖНО!
            server.quit() # Закрываю соединение с почтовым сервером

            

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')  # Для CORS
            self.end_headers()

            self.wfile.write(json.dumps({
                    "status": "success",
                    "message": f"Резюме отправлено на почту {send_to}, проверьте папку Спам"
                    }, ensure_ascii=False).encode('utf-8')) 


            self.write_logs(f'Письмо успешно отправлено', send_to)

        except Exception as ex:
            print('Error', str(ex))
            server.quit() # Закрываю соединение с почтовым сервером

            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "error",
                "message": str(ex)
            }

            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

            self.write_logs(f'Письмо не отправлено ошибка {ex}', send_to)

    
    @staticmethod
    def write_logs(result, mail='None'):

        with open(LOGS_PATH, 'a', encoding='utf-8') as file:
            file.write(result + ' ' + mail + '\n')


    def do_OPTIONS(self):

        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        print("✅ Сервер дал разрешение через OPTIONS")
        
        response = {
                "status": "OK",
                "message": 'OPTIONS'
            }

        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))




if __name__ == '__main__':
    
    server = HTTPServer(('0.0.0.0', 5002), MailHandler)
    print('Server run 0.0.0.0: 5002')
    server.serve_forever()

