import streamlit as st
from streamlit_lottie import st_lottie
import requests
import bs4
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import json

# st.set_page_config(page_title="Doki Doki Jobs", layout="wide")


def gaijinpot(palabra):
    resultados = []  # Lista para almacenar los resultados
    campos = ['Date', 'Company', 'Salary', 'Location']
    contador = 0  # Contador de trabajos encontrados
    url = f'https://jobs.gaijinpot.com/job/index/lang/en?keywords={palabra}&region=&english_ability=&language=&other_language=&career_level=&contract_type=&employer_type=&remote_work_ok=0&overseas_application=1&has_video_presentation=0'
    parsed_url = urlparse(url)
    if parsed_url.scheme and parsed_url.netloc:
        response = requests.get(url)
        content = response.text
        soup = bs4.BeautifulSoup(content, 'html.parser')
        pattern = re.compile(r'/job/view/lang/en/keywords/{}/overseas_application/1/job_id/\d+'.format(palabra))
        a_elements = soup.find_all('a', href=pattern)
        for a in a_elements:
            titulo = a.get_text(strip=True)
            if titulo:
                trabajo = {'Título': titulo}  # Diccionario para almacenar los detalles del trabajo
                job_link = "https://jobs.gaijinpot.com/" + a['href']
                trabajo['Enlace de trabajo'] = job_link
                dd_elements = a.find_all_next('dd')
                for nombre_campo, dd in zip(campos, dd_elements):
                    texto = dd.get_text(strip=True)
                    trabajo[nombre_campo] = texto
                resultados.append(trabajo)  # Agregar el trabajo a la lista de resultados
                contador += 1  # Incrementar el contador de trabajos encontrados
    else:
        resultados.append("No hay trabajos en GaijinPot.")
    return contador, resultados

def wantedly(palabra):
    resultados = []  # Lista para almacenar los resultados
    contador = 0  # Contador de trabajos encontrados

    # Construir la URL de búsqueda con la palabra clave proporcionada por el usuario
    url = f'https://sg.wantedly.com/projects?new=true&page=1&keywords={palabra}&order=mixed'

    # Comprobar si la URL es válida
    parsed_url = urlparse(url)
    if parsed_url.scheme and parsed_url.netloc:

        # Realizar la solicitud GET a la URL
        response = requests.get(url)

        content = response.text

        # Crear un objeto BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        job_items = soup.find_all('li', class_='ProjectListJobPostsLaptop__ProjectListItem-sc-79m74y-12')

        # Iterar sobre cada elemento de trabajo y extraer la información requerida
        for job_item in job_items:
            puesto_element = job_item.find('span', class_='FeatureTagList__TagLabelNormal-sc-lktsv0-5')
            if puesto_element:
                puesto = puesto_element.text.strip()
            else:
                puesto = None

            if puesto is None:
                break
            else:
                disponibilidad_elements = job_item.find_all('span', class_='FeatureTagList__TagLabelNormal-sc-lktsv0-5')
                if len(disponibilidad_elements) > 1:
                    disponibilidad = disponibilidad_elements[1].text.strip()
                else:
                    disponibilidad = None

                descripcion_element = job_item.find('p', class_='ProjectListJobPostItem__DescriptionText-sc-bjcnhh-7')
                if descripcion_element:
                    descripcion = descripcion_element.text.strip()
                else:
                    descripcion = None

                if puesto and descripcion:
                    requisitos_index = descripcion.find(puesto)
                    if requisitos_index != -1:
                        requisitos_start_index = requisitos_index + len(puesto) + 1
                        requisitos = descripcion[requisitos_start_index:].strip().split('\n\n')[0].strip()
                    else:
                        requisitos = None
                else:
                    requisitos = None

                empresa_element = job_item.find('p', class_='JobPostCompanyWithWorkingConnectedUser__CompanyNameText-sc-1nded7v-5')
                if empresa_element:
                    empresa = empresa_element.text.strip()
                else:
                    empresa = None

                # Obtener el enlace de trabajo
                enlace_trabajo = job_item.find('a', class_='ProjectListJobPostItem__ProjectLink-sc-bjcnhh-1')['href']
                job_link_complete = "https://sg.wantedly.com/" + enlace_trabajo

                # Agregar los detalles del trabajo a la lista de resultados
                trabajo = {
                    'Puesto': puesto,
                    'Disponibilidad': disponibilidad,
                    'Requisitos': requisitos,
                    'Empresa': empresa,
                    'Enlace de trabajo': job_link_complete
                }
                resultados.append(trabajo)

                # Incrementar el contador de trabajos encontrados
                contador += 1
    else:
        print("No hay trabajos en Wantedly.")

    return contador, resultados

def daijob(palabra):
    resultados = []  # Lista para almacenar los resultados
    contador = 0  # Contador de trabajos encontrados

    # Construir la URL de búsqueda con la palabra clave proporcionada por el usuario
    url = f'https://www.daijob.com/en/jobs/search_result?working_a_locations[]=230&working_a_locations[]=102&job_search_form_hidden=1&keywords={palabra}&ability_of_language=48'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    # Realizar la solicitud GET a la URL
    response = requests.get(url, headers=headers)

    content = response.text
    # Crear un objeto BeautifulSoup
    soup = bs4.BeautifulSoup(content, "html.parser")

    # Encontrar todos los elementos con la clase "jobs_box"
    jobs = soup.find_all("div", class_="jobs_box")

    # Iterar sobre cada trabajo y extraer la información
    for job in jobs:
        company_name_elem = job.find("div", class_="jobs_box_header_title")
        if company_name_elem and company_name_elem.a:
            company_name = company_name_elem.a.text.strip()
        else:
            company_name_link = job.find("td")
            company_name = company_name_link.text.strip() if company_name_link else "No existe"

        location_elem = job.find("a", href=lambda href: href and "la=" in href)
        location = location_elem.text.strip() if location_elem else "No location found"

        salary_elem = job.find("a", href=lambda href: href and "ns=" in href)
        salary = salary_elem.text.strip() if salary_elem else "No salary found"

        japanese_level_elem = job.find("a", href=lambda href: href and "ol" in href)
        japanese_level = japanese_level_elem.text.strip() if japanese_level_elem else "No Japanese level found"

        job_link_elem = job.find("a", href=True)
        job_link = job_link_elem["href"] if job_link_elem else "No job link found"
        job_link_complete = "https://www.daijob.com/" + job_link

        # Agregar los detalles del trabajo a la lista de resultados
        trabajo = {
            "Empresa": company_name,
            "Ubicación": location,
            "Salario": salary,
            "Nivel de japonés": japanese_level,
            "Enlace del trabajo": job_link_complete
        }
        resultados.append(trabajo)

        # Incrementar el contador de trabajos encontrados
        contador += 1

    return contador, resultados

def imprimir_resultados_gaijinpot(resultados):
    for trabajo in resultados:
        st.write(f"Título: {trabajo['Título']}")
        st.write(f"Empresa: {trabajo['Company']}")
        st.write(f"Salario: {trabajo['Salary']}")
        st.write(f"Ubicación: {trabajo['Location']}")
        st.write(f"Fecha: {trabajo['Date']}")
        st.write(f"Enlace de trabajo: {trabajo['Enlace de trabajo']}")
        st.write("------------------------")
        
def imprimir_resultados_wantedly(resultados):
    for trabajo in resultados:
        st.write(f"Puesto: {trabajo['Puesto']}")
        st.write(f"Empresa: {trabajo['Empresa']}")
        st.write(f"Requisitos: {trabajo['Requisitos']}")
        st.write(f"Disponibilidad: {trabajo['Disponibilidad']}")
        st.write(f"Enlace de trabajo: {trabajo['Enlace de trabajo']}")
        st.write("------------------------")

def imprimir_resultados_daijob(resultados):
    for trabajo in resultados:
        st.write(f"Empresa: {trabajo['Empresa']}")
        st.write(f"Ubicación: {trabajo['Ubicación']}")
        st.write(f"Salario: {trabajo['Salario']}")
        st.write(f"Nivel de japonés: {trabajo['Nivel de japonés']}")
        st.write(f"Enlace de trabajo: {trabajo['Enlace del trabajo']}")
        st.write("------------------------")

def scrapingDokiDoki(palabra):
    contador_gaijinpot, resultados_gaijinpot = gaijinpot(palabra)
    contador_wantedly, resultados_wantedly = wantedly(palabra)
    contador_daijob, resultados_daijob = daijob(palabra)

    contador = contador_gaijinpot + contador_wantedly + contador_daijob

    #imprimir_resultados_gaijinpot(resultados_gaijinpot)
    #imprimir_resultados_wantedly(resultados_wantedly)
    #imprimir_resultados_daijob(resultados_daijob)

    return contador, resultados_gaijinpot, resultados_wantedly, resultados_daijob

# def load_lottiefile(filepath: str):
#     with open(filepath, "r") as f:
#         return json.load(f)

# lottie_coding = load_lottiefile('Imágenes\Animation - 1715635226627.json')

def main():
    # Imagen centrada
    st.image("Imágenes/Logo Doki Doki.png", width=200)

    st.title("Encuentra tu trabajo aquí")
    palabra = st.text_input("Ingrese la palabra clave de búsqueda:")
    if st.button("Buscar"):
        if palabra:
            contador, resultados_gaijinpot, resultados_wantedly, resultados_daijob = scrapingDokiDoki(palabra)
            st.markdown(f'**Cantidad de trabajos encontrados con la palabra "{palabra}": {contador}**')
            imprimir_resultados_gaijinpot(resultados_gaijinpot)
            imprimir_resultados_wantedly(resultados_wantedly)
            imprimir_resultados_daijob(resultados_daijob)
        else:
            st.warning("Por favor, ingrese una palabra clave para la búsqueda.")

if __name__ == "__main__":
    main()

