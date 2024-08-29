import win32serviceutil
import win32service
import win32event
import servicemanager
import os
import time
import logging

SERVICE_NAME = "Cloudflared"  # Nome do serviço a ser monitorado
SERVICE_DISPLAY_NAME = "Monitor Cloudflared Service"
SERVICE_DESCRIPTION = "Serviço para monitorar e reiniciar o serviço Cloudflared."

class MonitorService(win32serviceutil.ServiceFramework):
    _svc_name_ = "MonitorCloudflaredService"
    _svc_display_name_ = SERVICE_DISPLAY_NAME
    _svc_description_ = SERVICE_DESCRIPTION

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

        # Configuração do logging
        logging.basicConfig(filename='C:\\Scripts\\service_monitor.log', level=logging.INFO, format='%(asctime)s %(message)s')

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ""))
        self.main()

    def main(self):
        while self.running:
            if not self.is_service_running(SERVICE_NAME):
                logging.warning(f"Serviço {SERVICE_NAME} está parado. Reiniciando...")
                self.restart_service(SERVICE_NAME)
            else:
                logging.info(f"Serviço {SERVICE_NAME} está rodando normalmente.")
            time.sleep(60)

    def is_service_running(self, service_name):
        try:
            status = os.popen(f'sc query {service_name} | find "RUNNING"').read().strip()
            return "RUNNING" in status
        except Exception as e:
            logging.error(f"Erro ao verificar o status do serviço: {e}")
            return False

    def restart_service(self, service_name):
        try:
            os.system(f'sc stop {service_name}')
            time.sleep(5)
            os.system(f'sc start {service_name}')
            logging.info(f"Serviço {service_name} reiniciado.")
        except Exception as e:
            logging.error(f"Erro ao reiniciar o serviço: {e}")

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MonitorService)
