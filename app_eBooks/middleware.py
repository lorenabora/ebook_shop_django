from datetime import datetime
from .views import log_access, Accesare
from .tracker import page_counter

class IPMiddle:
    def __init__(self, get_response):
        self.get_response = get_response    #optin raspuns din view, forteaza apelarea si optine raspunsul

    def get_ip(self,request):
            # req_headers = request.META
            str_lista_ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if str_lista_ip:
                return str_lista_ip.split(',')[0].strip()
            return request.META.get('REMOTE_ADDR') 
        
    def __call__(self, request):
        # cod de procesare a cererii ....      
        #putem trimite date către funcția de vizualizare; le setăm ca proprietăți în request 
        ### aici e get_ip...    
        # request.proprietate_noua=17  
        
        request.client_ip = self.get_ip(request)
        
        now = datetime.now()
        request.timestamp_str = now.strftime('%Y-%m-%d %H:%M:%S')
        
        if request.path != "/favicon.ico":
            ### logare access inainte de view   
            # clear_path=Accesare.pagina(request.path)
            acc=Accesare(request.META.get("REMOTE_ADDR"), request.path, now)
            log_access.append(acc)
            # incrementez nr de accesari per pagina
            page_counter[request.path]+=1
            # se apelează (indirect) funcția de vizualizare (din views.py)
            response = self.get_response(request)      

        # putem adauga un header HTTP pentru toate răspunsurile
        response['header_nou'] = 'valoare'
        # aici putem modifica chiar conținutul răspunsului
        # verificăm tipul de conținut folosind headerul HTTP Content-Type
        # motivul fiind că putem transmite și alte resurse (imagini, css etc.), nu doar fișiere html
        if response.has_header('Content-Type') and 'text/html' in response['Content-Type']:
           
            # obținem conținutul
            # (response.content este memorat ca bytes, deci îl transformăm în string)
            content = response.content.decode('utf-8')
           
            # Modificăm conținutul
            # new_content = content.replace(
            #     '</body>',
            #     '<div>Continut suplimentar</div></body>'
            # )
           
            # Suprascriem conținutul răspunsului
            # response.content = new_content.encode('utf-8')
           
            # Actualizăm lungimea conținutului (obligatoriu, fiind header HTTP)
            # response['Content-Length'] = len(response.content)
       
        return response