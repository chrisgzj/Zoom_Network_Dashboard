import http.client
import json
import time
from urllib.parse import quote

conn = http.client.HTTPSConnection("api.zoom.us")
headers = {
    'authorization': "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOm51bGwsImlzcyI6IjZjcVczdTJpUXBTd2loUkdVYkoxMGciLCJleHAiOjE2MDkzOTQ0MDAsImlhdCI6MTYwNDE5NjM0Nn0.Hh5PqTPXuPFGgtomj97tvNT85udw_IvexQQTGpMCu2c",
    'content-type': "application/json"
    }

def bajar_reuniones():
    link_basic = "/v2/metrics/meetings?type=past&from=2020-10-01&to=2020-10-31&page_size=300"
    reuniones = []
    next_page = ''
    contador = 0
    while next_page != '' or reuniones == []:
        if next_page == '':
            conn.request("GET", link_basic, headers=headers)
        else:
            conn.request("GET", link_basic + "&next_page_token=" + next_page, headers=headers)
        res = conn.getresponse()
        datos = json.load(res)
        print(datos)
        [reuniones.append(reu) for reu in datos['meetings']]
        next_page = datos['next_page_token']
        contador += 1
        print(contador)
        time.sleep(2)
    with open('reuniones_oct.json', 'w') as outfile:
        json.dump(reuniones, outfile)

def filtrar_reuniones():
    with open('reuniones_oct.json', 'r') as infile:
        reuniones = json.load(infile)
    with open('ids_clases.json', 'r') as infile:
        ids_clases = json.load(infile)
    reuniones_clase = [reu for reu in reuniones if reu['id'] in ids_clases]
    print(len(reuniones_clase))
    print(reuniones_clase[0])
    with open('reunionesclase_oct.json', 'w') as outfile:
        json.dump(reuniones_clase, outfile)

def bajar_participantes():
    with open('reunionesclase_oct.json', 'r') as infile:
        reuniones = json.load(infile)

    uuids = [reu['uuid'] for reu in reuniones]

    participantes = {}

    uuids = uuids[1227:] #Dice que el 1226 no existe!
    print(len(uuids))

    for uuid in uuids:
        encoded_uuid = quote(uuid, safe='')
        double_encoded = quote(encoded_uuid, safe='')
        link = "/v2/metrics/meetings/" + double_encoded +"/participants?type=past&page_size=300"
        conn.request("GET", link, headers=headers)
        res = conn.getresponse()
        datos = json.load(res)
        print(datos)
        next_page = datos['next_page_token']
        list_participantes = datos['participants']
        while (next_page != ''):
            conn.request("GET", link + "&next_page_token=" + next_page, headers=headers)
            res = conn.getresponse()
            datos = json.load(res)
            next_page = datos['next_page_token']
            [list_participantes.append(dato) for dato in datos['participants']]
        print(datos['total_records'], " vs. ", len(list_participantes))
        participantes[uuid] = list_participantes
        with open('participantes_oct.json', 'w') as outfile:
            json.dump(participantes, outfile)
        time.sleep(1)

def extraer_fallas():
    with open('participantes_oct.json', 'r') as infile:
        participantes = json.load(infile)
    individuales = []
    [[individuales.append(part) for part in ls] for ls in participantes.values()]
    print(len(individuales))
    razones = {}
    razones['sin_razon'] = 0
    razones['razon_vacia'] = 0
    fallas = []
    for indiv in participantes:
        indi = participantes[indiv]
        for ind in indi:
            if 'leave_reason' in ind:
                razon = ind['leave_reason']
                if razon != '':
                    razon = razon[razon.index("<br>") + 12:]
                    if razon in razones:
                        razones[razon] += 1
                    else:
                        razones[razon] = 1
                else:
                    razones['razon_vacia'] += 1
                if razon == 'Network connection error. ':
                    ind['meeting_uuid'] = indiv
                    # participantes[indiv]['meeting_id'] = indiv
                    fallas.append(ind)
            else:
                razones['sin_razon'] += 1
    print(razones)
    # with open('participantes_oct.json', 'w') as outfile:
    #     json.dump(particip1, outfile)
    print(len(fallas))
    print(fallas[0])




# participantes = datos["participants"]
# for part in participantes:
#     print(part['leave_reason'])

extraer_fallas()
# bajar_participantes()