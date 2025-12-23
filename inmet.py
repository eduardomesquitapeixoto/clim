import time
import random
import pandas as pd
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# ============================================
# CONFIGURAÇÕES INICIAIS
# ============================================

# Verificar se o Chrome está instalado
try:
    chrome_version = subprocess.check_output(['google-chrome', '--version'], stderr=subprocess.STDOUT)
    print(f"✓ Chrome encontrado: {chrome_version.decode().strip()}")
except:
    try:
        chrome_version = subprocess.check_output(['chromium', '--version'], stderr=subprocess.STDOUT)
        print(f"✓ Chromium encontrado: {chrome_version.decode().strip()}")
    except:
        print("✗ Chrome/Chromium não encontrado. Instale com: sudo apt install google-chrome-stable")
        exit(1)

# Configuração avançada do WebDriver
chrome_options = Options()

# Opções essenciais para headless
# chrome_options.add_argument('--headless=new')  # Novo modo headless
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920,1080')

# Opções para estabilidade
chrome_options.add_argument('--disable-software-rasterizer')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-background-networking')
chrome_options.add_argument('--disable-default-apps')
chrome_options.add_argument('--disable-sync')
chrome_options.add_argument('--disable-translate')
chrome_options.add_argument('--disable-background-timer-throttling')
chrome_options.add_argument('--disable-renderer-backgrounding')
chrome_options.add_argument('--disable-backgrounding-occluded-windows')
chrome_options.add_argument('--disable-client-side-phishing-detection')
chrome_options.add_argument('--disable-crash-reporter')
chrome_options.add_argument('--disable-oopr-debug-crash-dump')
chrome_options.add_argument('--no-crash-upload')
chrome_options.add_argument('--disable-breakpad')
chrome_options.add_argument('--disable-component-update')
chrome_options.add_argument('--allow-pre-commit-input')
chrome_options.add_argument('--autoplay-policy=user-gesture-required')
chrome_options.add_argument('--disable-domain-reliability')
chrome_options.add_argument('--disable-features=AudioServiceOutOfProcess,AudioServiceSandbox')
chrome_options.add_argument('--disable-hang-monitor')
chrome_options.add_argument('--disable-ipc-flooding-protection')
chrome_options.add_argument('--disable-notifications')
chrome_options.add_argument('--disable-prompt-on-repost')
chrome_options.add_argument('--disable-site-isolation-trials')
chrome_options.add_argument('--disable-web-security')
chrome_options.add_argument('--force-color-profile=srgb')
chrome_options.add_argument('--metrics-recording-only')
chrome_options.add_argument('--mute-audio')

# Opções para evitar detecção
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument('--disable-blink-features=AutomationControlled')

# Configurações de preferências
prefs = {
    'profile.default_content_setting_values': {
        'images': 2,  # 0=Permitir, 1=Bloquear, 2=Bloquear imagens de terceiros
        'javascript': 1,  # Permitir JavaScript
    },
    'profile.managed_default_content_settings.images': 2
}
chrome_options.add_experimental_option('prefs', prefs)

# ============================================
# LISTA DE MUNICÍPIOS
# ============================================

municipios = [
    '3300100', '3300159', '3300209', '3300225', '3300233', '3300258', '3300308',
    '3300407', '3300456', '3300506', '3300605', '3300704', '3300803', '3300902',
    '3300936', '3300951', '3301009', '3301108', '3301157', '3301207', '3301306',
    '3301405', '3301504', '3301603', '3301702', '3301801', '3301850', '3301876',
    '3301900', '3302007', '3302056', '3302106', '3302205', '3302254', '3302270',
    '3302304', '3302403', '3302452', '3302502', '3302601', '3302700', '3302809',
    '3302858', '3302908', '3303005', '3303104', '3303203', '3303302', '3303401',
    '3303500', '3303609', '3303708', '3303807', '3303856', '3303906', '3303955',
    '3304003', '3304102', '3304110', '3304128', '3304144', '3304151', '3304201',
    '3304300', '3304409', '3304508', '3304524', '3304557', '3304607', '3304706',
    '3304755', '3304805', '3304904', '3305000', '3305109', '3305133', '3305158',
    '3305208', '3305307', '3305406', '3305505', '3305554', '3305604', '3305703',
    '3305752', '3305802', '3305901', '3306008', '3306107', '3306156', '3306206',
    '3306305'
]

print(f"Total de municípios a processar: {len(municipios)}")

# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def criar_driver():
    """Cria um novo driver do Chrome com tratamento de erros"""
    tentativas = 0
    max_tentativas = 3
    
    while tentativas < max_tentativas:
        try:
            tentativas += 1
            print(f"\nTentativa {tentativas} de criar o driver...")
            
            # Usar Service para melhor controle
            service = Service()
            
            # Tentar com opções diferentes
            if tentativas > 1:
                # Na segunda tentativa, tentar sem headless primeiro para debug
                chrome_options_tentativa = Options()
                chrome_options_tentativa.add_argument('--no-sandbox')
                chrome_options_tentativa.add_argument('--disable-dev-shm-usage')
                chrome_options_tentativa.add_argument('--window-size=1920,1080')
                
                if tentativas == 2:
                    print("Tentando modo NÃO headless...")
                    # Modo não headless para debug
                else:
                    print("Tentando modo headless com menos opções...")
                    chrome_options_tentativa.add_argument('--headless=new')
                
                driver = webdriver.Chrome(service=service, options=chrome_options_tentativa)
            else:
                driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Configurar timeouts
            driver.set_page_load_timeout(60)
            driver.implicitly_wait(10)
            
            # Executar script para evitar detecção
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✓ Driver criado com sucesso!")
            return driver
            
        except Exception as e:
            print(f"✗ Erro ao criar driver (tentativa {tentativas}): {type(e).__name__}")
            if tentativas < max_tentativas:
                print(f"Aguardando 5 segundos antes de tentar novamente...")
                time.sleep(5)
            else:
                print("\nNão foi possível criar o driver. Verifique:")
                print("1. Se o Chrome está instalado: sudo apt install google-chrome-stable")
                print("2. Se o chromedriver está instalado: sudo apt install chromium-chromedriver")
                print("3. Ou use: pip install webdriver-manager")
                raise

def processar_municipio(driver, municipio, datas):
    """Processa um município individual"""
    url = f"https://previsao.inmet.gov.br/{municipio}"
    
    try:
        driver.get(url)
        
        # Aguardar carregamento com timeout maior
        wait = WebDriverWait(driver, 30)
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section.grid.grid-template-columns-4"))
        )
        
        # Pequena pausa para renderização completa
        time.sleep(1.5)
        
        sections = driver.find_elements(By.CSS_SELECTOR, "section.grid.grid-template-columns-4")
        
        resultados = []
        
        for idx_section, section in enumerate(sections[:5]):  # Apenas 5 dias
            try:
                section_text = section.text.split("\n")
                
                temp_min = None
                temp_max = None
                
                # Buscar temperaturas
                for i in range(len(section_text)):
                    if "Temperatura Mínima" in section_text[i]:
                        temp_min = section_text[i + 1] if (i + 1) < len(section_text) else ''
                    if "Temperatura Máxima" in section_text[i]:
                        temp_max = section_text[i + 1] if (i + 1) < len(section_text) else ''
                
                if temp_min and temp_max:
                    resultados.append({
                        'Código Município': municipio,
                        'Data': datas[idx_section].strftime('%Y-%m-%d'),
                        'Temperatura Mínima': temp_min.strip(),
                        'Temperatura Máxima': temp_max.strip()
                    })
                    
            except Exception as e:
                print(f"    Erro no bloco {idx_section}: {e}")
                continue
        
        return resultados
        
    except TimeoutException:
        print(f"    Timeout ao carregar {municipio}")
        return []
    except Exception as e:
        print(f"    Erro geral: {type(e).__name__}: {str(e)[:100]}")
        return []

# ============================================
# EXECUÇÃO PRINCIPAL
# ============================================

def main():
    """Função principal de execução"""
    print("=" * 80)
    print("INICIANDO COLETA DE DADOS DO INMET")
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Criar driver
    try:
        driver = criar_driver()
    except Exception as e:
        print(f"\n✗ FALHA CRÍTICA: Não foi possível iniciar o Chrome: {e}")
        print("\nTente executar no modo NÃO headless primeiro para testar:")
        print("1. Remova a linha: chrome_options.add_argument('--headless=new')")
        print("2. Execute novamente o script")
        return
    
    # Preparar datas
    hoje = datetime.today()
    datas = [hoje + timedelta(days=i) for i in range(5)]
    
    # Lista para armazenar dados
    dados = []
    
    # Configurações
    ESPERA_MIN = 3
    ESPERA_MAX = 8
    MAX_TENTATIVAS = 8
    
    # Processar municípios
    for idx, municipio in enumerate(municipios, 1):
        print(f"\n[{idx:03d}/{len(municipios):03d}] Município: {municipio}")
        
        tentativa = 1
        sucesso = False
        
        while tentativa <= MAX_TENTATIVAS and not sucesso:
            try:
                if tentativa > 1:
                    espera = random.uniform(2, 5)
                    print(f"  Tentativa {tentativa}/{MAX_TENTATIVAS} (espera: {espera:.1f}s)")
                    time.sleep(espera)
                
                resultados = processar_municipio(driver, municipio, datas)
                
                if resultados:
                    dados.extend(resultados)
                    print(f"  ✓ {len(resultados)} dias coletados")
                    sucesso = True
                else:
                    print(f"  ✗ Nenhum dado coletado na tentativa {tentativa}")
                    tentativa += 1
                    
            except WebDriverException as e:
                print(f"  ✗ Erro WebDriver (tentativa {tentativa}): {type(e).__name__}")
                
                # Tentar recriar o driver
                if "session" in str(e).lower() or "chrome" in str(e).lower():
                    print("  Recriando driver...")
                    try:
                        driver.quit()
                    except:
                        pass
                    
                    time.sleep(5)
                    try:
                        driver = criar_driver()
                    except:
                        print("  Não foi possível recriar o driver")
                        break
                
                tentativa += 1
                
            except Exception as e:
                print(f"  ✗ Erro inesperado (tentativa {tentativa}): {type(e).__name__}")
                tentativa += 1
        
        # Salvar backup a cada 10 municípios
        if idx % 10 == 0 and dados:
            try:
                df_temp = pd.DataFrame(dados)
                df_temp.to_csv('temperatura_inmet_backup.csv', index=False, encoding='utf-8')
                print(f"\n  💾 Backup salvo: {len(dados)} registros")
            except Exception as e:
                print(f"  ✗ Erro ao salvar backup: {e}")
        
        # Espera entre municípios
        if idx < len(municipios):
            espera_mun = random.uniform(ESPERA_MIN, ESPERA_MAX)
            print(f"  ⏳ Aguardando {espera_mun:.1f}s...")
            time.sleep(espera_mun)
    
    # Fechar driver
    try:
        driver.quit()
        print("\n✓ Driver finalizado")
    except:
        pass
    
    # Processar resultados
    print("\n" + "=" * 80)
    print("PROCESSAMENTO CONCLUÍDO!")
    print("=" * 80)
    
    if dados:
        # Criar DataFrame
        df = pd.DataFrame(dados)
        
        # Estatísticas
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   Total de registros: {len(df)}")
        print(f"   Municípios com dados: {df['Código Município'].nunique()}")
        print(f"\n   Distribuição por dia:")
        
        dias_counts = df['Data'].value_counts().sort_index()
        for dia, count in dias_counts.items():
            print(f"     {dia}: {count:3d} registros")
        
        # Salvar dados
        try:
            # CSV principal
            df.to_csv('temperatura_inmet.csv', index=False, encoding='utf-8')
            print(f"\n💾 Dados salvos em: temperatura_inmet.csv")
            
            # CSV com timestamp para backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            df.to_csv(f'temperatura_inmet_{timestamp}.csv', index=False, encoding='utf-8')
            print(f"📂 Backup salvo em: temperatura_inmet_{timestamp}.csv")
            
            # Exibir amostra
            print(f"\n📄 AMOSTRA DOS DADOS (primeiras 5 linhas):")
            print(df.head().to_string())
            
        except Exception as e:
            print(f"\n✗ Erro ao salvar arquivos: {e}")
            print(f"Dados coletados (últimos 5 registros):")
            print(pd.DataFrame(dados[-5:]).to_string())
    else:
        print("\n✗ Nenhum dado foi coletado!")
        print("\nPossíveis soluções:")
        print("1. Verifique sua conexão com a internet")
        print("2. Tente executar sem modo headless primeiro")
        print("3. Verifique se o site https://previsao.inmet.gov.br está acessível")
    
    print(f"\n🏁 Término: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

# ============================================
# EXECUTAR
# ============================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n\n💥 ERRO NÃO TRATADO: {type(e).__name__}")
        print(f"Detalhes: {e}")
        print("\nPara suporte:")
        print("1. Execute: pip install --upgrade selenium")
        print("2. Verifique: sudo apt install google-chrome-stable chromium-chromedriver")
    finally:
        print("\nScript finalizado.")
