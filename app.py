# BIBLIOTECAS
from flask import Flask, render_template, request, redirect, url_for, session
import requests, json, random

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "sua_chave_secreta_aqui"

# ENDPOINT
API_BASE_URL = "https://projetoa3-glitch.glitch.me"
    # GET
POKEMON_ENDPOINT = "/api/pokemon/"
GET_NEXTROUND_ENDPOINT = '/api/proximarodada'
GET_LASTGAME_ENDPOINT = '/api/ultimojogo/'
GET_RESULTMATCH_ENDPOINT = '/api/resultadopartida'
GET_HISTORYMATCH_ENDPOINT = '/api/resultadogeral'
    # POST
LOGIN_ENDPOINT = "/api/login"
CREATE_USER_ENDPOINT = "/api/usuario"
CREATE_MATCH_ENDPOINT = "/api/partida"
CREATE_RESULT_ENDPOINT = "/api/resultado"
CREATE_ROUND_ENDPOINT = "/api/rodada"
    # PATCH
PATCH_USER_ENDPOINT = "/api/usuario/"
PATCH_MATCH_ENDPOINT = '/api/partida'
PATCH_RESULT_ENDPOINT = '/api/resultado'
PATCH_ROUND_ENDPOINT = '/api/rodada'
PATCH_MATCHCLEAR_ENPOINT = '/api/partidalimpa'
PATCH_RESULTMATCH_ENDPOINT = '/api/gravarpartida'
    # DELETE
DELETE_USER_ENDPOINT = "/api/usuario"

# FUNÇÕES

# Função: valida_acesso
# Descrição: Valida se o usuário está autenticado com email e token na sessão.
# Tipo: Função
# Histórico:
def valida_acesso():

    email = session.get('email')
    token = session.get('token')
    if not email or not token:
        session.clear()
        return False

    return True

# Função: comprar_cartas
# Descrição: Compra cartas de Pokémon para o jogador e o CPU, atribuindo-os de forma alternada.
# Tipo: Função
# Histórico:
def comprar_cartas():
    
    # Variável
    id_pkm_player = []
    id_pkm_cpu = []
    complet_pkm_player = []
    complet_pkm_cpu = []
    j = 1
    random_ids = random.sample(range(1, 152), 12)

    # GET Pokémon e grava em sessão
    for i in random_ids:
        token = session.get('token')
        headers = {"x-access-token": token}
        response = requests.get(f"{API_BASE_URL}{POKEMON_ENDPOINT}{i}",headers=headers)
        
        if response.status_code == 200:
            pokemon_data = response.json()
            try:
                pokemon_data['usado'] = 2
                if j % 2 == 0 :
                    id_pkm_player.append(pokemon_data["id"])
                    complet_pkm_player.append(pokemon_data)
                else:
                    id_pkm_cpu.append(pokemon_data["id"])
                    complet_pkm_cpu.append(pokemon_data)
            except requests.exceptions.JSONDecodeError:
                print(f"Erro ao decodificar JSON para Pokémon com ID {i}. Resposta: {response.text}")
        else:
            print(f"Erro na requisição para Pokémon com ID {i}. Código de status: {response.status_code}")
        j += 1

    session['id_pkm_player'] = id_pkm_player
    session['id_pkm_cpu'] = id_pkm_cpu
    session['complet_pkm_player'] = complet_pkm_player
    session['complet_pkm_cpu'] = complet_pkm_cpu

    print("***COMPRA DE CARTAS*** ", complet_pkm_player, " - ", complet_pkm_cpu) # PRINT CONSOLE

    return id_pkm_player, id_pkm_cpu

# Função: grava_partida
# Descrição: Grava uma nova partida no banco de dados com os IDs dos Pokémon do jogador e do CPU.
# Tipo: Função
# Histórico:
def grava_partida(id_pkm_player, id_pkm_cpu):

    # Variável
    email = session.get('email')
    token = session.get('token')
    headers = {"x-access-token": token}
    data = {"email":email,"player":id_pkm_player,"cpu":id_pkm_cpu}

    # POST tabela partida
    response = requests.post(f"{API_BASE_URL}{CREATE_MATCH_ENDPOINT}", json=data, headers=headers)
    user_data = response.json()
    session['id_partida'] = user_data.get('id')
    partida=session['id_partida']
    
    print("***GRAVA PARTIDA*** ", partida) # PRINT CONSOLE

    return

# Função: grava_resultado
# Descrição: Grava os resultados das partidas, associando os Pokémon do jogador e do CPU a uma partida.
# Tipo: Função
# Histórico:
def grava_resultado():
    
    # Variável
    id_partida = session.get('id_partida')
    token = session.get('token')
    headers = {"x-access-token": token}
    id_pkm_player = session.get('id_pkm_player')
    id_pkm_cpu = session.get('id_pkm_cpu')

    # POST tabela resultado
    for i in range(6):
        data = {"id_partida": id_partida, "id_pokemon": id_pkm_player[i], "player": 1, "usado": 2 }
        requests.post(f"{API_BASE_URL}{CREATE_RESULT_ENDPOINT}", json=data, headers=headers)
    for i in range(6):
        data = {"id_partida": id_partida, "id_pokemon": id_pkm_cpu[i], "player": 2, "usado": 2 }
        requests.post(f"{API_BASE_URL}{CREATE_RESULT_ENDPOINT}", json=data, headers=headers)
    
    print("***GRAVA RESULTADO*** Não tem retorno no JSON") # PRINT CONSOLE

    return

# Função: grava_rodada
# Descrição: Grava a rodada da partida e o jogador que iniciou.
# Tipo: Função
# Histórico:
def grava_rodada():
    
    # Variável
    token = session.get('token')
    headers = {"x-access-token": token}
    id_partida = session.get('id_partida')
    random_begin = random.randint(1, 2)
    data = {"id_partida": id_partida, "rodada": 1, "player_begin": random_begin}

    # POST tabela rodada
    response = requests.post(f"{API_BASE_URL}{CREATE_ROUND_ENDPOINT}", json=data, headers=headers)
    user_data = response.json()
    session['rodada'] = user_data.get('rodada')
    session['player_begin'] = user_data.get('player_begin')
    rodada=session['rodada']
    player_begin=session['player_begin']

    print("***GRAVA RODADA*** ", rodada, " - ",player_begin) # PRINT CONSOLE

    return

# Função: ultimo_jogo
# Descrição: Recupera o último jogo aberto de um jogador.
# Tipo: Função
# Histórico:
def ultimo_jogo(email):
    
    # Variável
    token = session.get('token')
    headers = {"x-access-token": token}

    # GET último jogo aberto
    response = requests.get(f"{API_BASE_URL}{GET_LASTGAME_ENDPOINT}{email}", headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        session['id_ultimo_jogo'] = user_data.get('id')
        id_ultimo_jogo = session['id_ultimo_jogo']

        print("***ÚLTIMO JOGO ABERTO*** ", id_ultimo_jogo) # PRINT CONSOLE

        return response.json()

    print("***ÚLTIMO JOGO ABERTO*** - SEM NENHUM JOGO ABERTO") # PRINT CONSOLE

    return None

# Função: proxima_rodada
# Descrição: Obtém as informações para a próxima rodada, separando os Pokémon do jogador e do CPU.
# Tipo: Função
# Histórico:
def proxima_rodada(id_partida, email):

    # Variável
    id_pkm_player = []
    complet_pkm_player = []
    id_pkm_cpu = []
    complet_pkm_cpu = []
    rodada =[]
    token = session.get('token')
    headers = {"x-access-token": token}

    # GET próxima rodada
    response = requests.get(f"{API_BASE_URL}{GET_NEXTROUND_ENDPOINT}", json={"id_partida": id_partida, "email": email}, headers=headers)
    pokemon_data = response.json()

    if response.status_code == 200:
        for index, pokemon in enumerate(pokemon_data):
            if index == 0:
                player_begin = pokemon['player_begin']
                rodada = pokemon['rodada']
            if pokemon['player'] == 1:
                id_pkm_player.append(pokemon['id'])
                complet_pkm_player.append(pokemon)
            else:
                id_pkm_cpu.append(pokemon['id'])
                complet_pkm_cpu.append(pokemon)
    else:
        print(f"Erro de comunicação. Código de status: {response.status_code}")

    session['id_pkm_player'] = id_pkm_player
    session['id_pkm_cpu'] = id_pkm_cpu
    session['complet_pkm_player'] = complet_pkm_player
    session['complet_pkm_cpu'] = complet_pkm_cpu
    session['player_begin'] = player_begin
    session['rodada'] = rodada

    print("***PRÓXIMA RODADA *** ", rodada, " - ",id_pkm_player, " - ", id_pkm_cpu) # PRINT CONSOLE

    return 

# Função: grava_turno
# Descrição: Grava o turno da partida, incluindo o resultado e a rodada.
# Tipo: Função
# Histórico:
def grava_turno(id_partida, resultado, id_pokemon, id_pokemon_cpu, rodada, player_begin):

    # Variável
    token = session.get('token')
    headers = {"x-access-token": token}
    rodada_result = rodada
    rodada_round = rodada + 1

    if player_begin == 1:
        player_begin = 2
    else:
        player_begin = 1

    #PATCH para as tabelas resultado e rodada
    requests.patch(f"{API_BASE_URL}{PATCH_RESULT_ENDPOINT}", json={"id_partida": id_partida, "id_pokemon": id_pokemon, "player": 1, "rodada": rodada_result, "usado": 1, "resultado": resultado}, headers=headers)
    requests.patch(f"{API_BASE_URL}{PATCH_RESULT_ENDPOINT}", json={"id_partida": id_partida, "id_pokemon": id_pokemon_cpu, "player": 2, "rodada": rodada_result, "usado": 1, "resultado": resultado}, headers=headers)
    requests.patch(f"{API_BASE_URL}{PATCH_ROUND_ENDPOINT}", json={"rodada": rodada_round, "player_begin": player_begin, "id_partida": id_partida}, headers=headers)
    
    print("***GRAVA TURNO***: ", id_partida, " - ", resultado, " - ",id_pokemon, " - ",id_pokemon_cpu, " - ",rodada, " - ",player_begin)

    return None

# Função: escolha_IA
# Descrição: Escolhe o melhor Pokémon da IA com base no atributo do jogador ou aleatoriamente.
# Tipo: Função
# Histórico:
def escolha_IA(complet_pkm_cpu, atributo_jogador=None):

    #Variável
    melhor_pokemon = None
    melhor_valor = -1
    atributo_escolhido = None

    # Início IA
    if atributo_jogador:  # Resposta da IA ao jogador
        for pokemon in complet_pkm_cpu:
            if pokemon[atributo_jogador] > melhor_valor and pokemon['usado'] == 2:
                melhor_pokemon = pokemon
                melhor_valor = pokemon[atributo_jogador]
        atributo_escolhido = atributo_jogador
    else:  # Caso a IA inicie o turno
        for pokemon in complet_pkm_cpu:
            for atributo, valor in pokemon.items():
                if atributo not in ['id', 'nome', 'player', 'rodada', 'usado', 'id_partida', 'player_begin'] and valor > melhor_valor and pokemon['usado'] == 2:
                    melhor_pokemon = pokemon
                    melhor_valor = valor
                    atributo_escolhido = atributo

    session['melhor_pokemon'] = melhor_pokemon
    session['atributo_escolhido'] = atributo_escolhido

    print("***ESCOLHA DA IA*** ", melhor_pokemon, " - ", atributo_escolhido) # PRINT CONSOLE

    return melhor_pokemon, atributo_escolhido

# Função: batalha
# Descrição: Realiza a batalha entre o Pokémon do jogador e o do CPU, comparando os atributos.
# Tipo: Função
# Histórico:
def batalha(pokemon_id, melhor_pokemon, atributo_escolhido):

    # Variável
    token = session.get('token')
    headers = {"x-access-token": token}

    # GET Pokémon escolhidos (Player e CPU)
    response_player = requests.get(f"{API_BASE_URL}{POKEMON_ENDPOINT}{pokemon_id}", headers=headers)
    response_cpu = requests.get(f"{API_BASE_URL}{POKEMON_ENDPOINT}{melhor_pokemon}", headers=headers)
    if response_player.status_code == 200 and response_cpu.status_code == 200:
        data_player = response_player.json()
        data_cpu = response_cpu.json()
        valor_player = data_player[atributo_escolhido]
        valor_cpu = data_cpu[atributo_escolhido]

    # Teste do resultado
    if valor_player > valor_cpu:
        print("***RESULTADO DA RODADA *** PLAYER GANHOU , ", atributo_escolhido, " - ", valor_player, " - ", valor_cpu)
        return 1  # Vitoria Player
    elif valor_cpu > valor_player:
        print("***RESULTADO DA RODADA *** CPU GANHOU , ", atributo_escolhido, " - ", valor_player, " - ", valor_cpu)
        return 2  # Vitoria CPU
    else:
        print("***RESULTADO DA RODADA *** EMPATE , ", atributo_escolhido, " - ", valor_player, " - ", valor_cpu)
        return 3 # Empate

# Função: gravar_final
# Descrição: Grava o resultado final da partida, determinando o vencedor com base nas rodadas.
# Tipo: Função
# Histórico:
def gravar_final():

    # Variável
    token = session.get('token')
    headers = {"x-access-token": token}
    resultado = ''
    id_partida = session.get('id_partida')

    # Define o id_partida (If para casos que o jogador recupera partida)
    if id_partida == '' or id_partida is None:
        id_partida = session['id_ultimo_jogo']
    else:
        id_partida = session['id_partida']

    # GET para pegar o resultado das rodadas e definir o vencedor
    response_resultado_partida = requests.get(f"{API_BASE_URL}{GET_RESULTMATCH_ENDPOINT}", json={"id_partida": id_partida}, headers=headers)
    resultado_partida = response_resultado_partida.json()
    session['resultado_partida'] = resultado_partida
    
    resultado_partida = session.get('resultado_partida', {})                                
    resultado_partida_V = resultado_partida.get('Player', 0)
    resultado_partida_D = resultado_partida.get('CPU', 0)
    
    # Calculo do resultado da partida
    if resultado_partida_V > resultado_partida_D:
        resultado = 1
    else:
        if resultado_partida_V < resultado_partida_D:
            resultado = 2
        else:
            resultado = 3 

    # PATCH para gravar o resultado da partida
    requests.patch(f"{API_BASE_URL}{PATCH_RESULTMATCH_ENDPOINT}", json={"resultado": resultado, "id": id_partida}, headers=headers)

    print('***GRAVA RESULTADO DA PARTIDA*** ', id_partida, " - ",resultado) # PRINT CONSOLE

    return

# Função: historico_partidas
# Descrição: Recupera e exibe o histórico de partidas do usuário.
# Tipo: Função
# Parâmetros de entrada: Nenhum
# Histórico: 
def historico_partidas():

    # Variável
    email = session.get('email')
    token = session.get('token')
    headers = {"x-access-token": token}

    # GET do histórico de partidas do usuário
    response_resultado_geral = requests.get(f"{API_BASE_URL}{GET_HISTORYMATCH_ENDPOINT}", json={"email": email}, headers=headers)
    resultado_geral = response_resultado_geral.json()
    session['resultado_geral'] = resultado_geral

    print("***HISTÓRICO DE PARTIDAS DO USUÁRIO***") # PRINT CONSOLE

    return

# ROTAS HTML

# Rota: /
# Descrição: Exibe a página inicial do site.
# Tipo: Rota
# Histórico: 
@app.route('/')
def index():

    return render_template('index.html')

# Rota: /login
# Descrição: Realiza o login do usuário.
# Tipo: Rota
# Histórico: 
@app.route('/login', methods=['GET', 'POST']) 
def login():

    if request.method == 'POST':
        email = request.form.get("email")
        senha = request.form.get("senha")
        response = requests.post(f"{API_BASE_URL}{LOGIN_ENDPOINT}", json={"email": email, "senha": senha})
        if response.status_code == 200:
            user_data = response.json() # Recebe JSON de retorno
            session['nome'] = user_data.get('nome') # Persiste o dado nome do JSON de retorno
            session['email'] = user_data.get('email')
            session['token'] = user_data.get('token')
            return redirect(url_for('menu'))
        else:
            return render_template('login.html', error="Erro de login.")

    return render_template('login.html')

# Rota: /criar_conta
# Descrição: Cria uma nova conta para o usuário.
# Tipo: Rota
# Histórico: 
@app.route('/criar_conta', methods=['GET', 'POST'])
def criar_conta():

    if request.method == 'POST':
        data = {"email": request.form.get("email"), "nome": request.form.get("nome"), "senha": request.form.get("senha")}
        response = requests.post(f"{API_BASE_URL}{CREATE_USER_ENDPOINT}", json=data)
        if response.status_code == 201:
            return render_template('login.html')
        else:
            return "Erro ao criar conta."

    return render_template('criar_conta.html')

# Rota: /deletar_conta
# Descrição: Deleta a conta do usuário após confirmação da senha.
# Tipo: Rota
# Histórico:
@app.route('/deletar_conta', methods=['GET', 'POST'])
def deletar_conta():

    nome_usuario = session.get('nome', 'Sem Nome')
    if not valida_acesso():
        return redirect(url_for('index'))
    if request.method == 'POST':
        senha = request.form.get("senha")
        email = session.get('email')
        token = session.get('token')
        headers = {"x-access-token": token}
        response = requests.delete(f"{API_BASE_URL}{DELETE_USER_ENDPOINT}", json={"email": email, "senha": senha}, headers=headers)
        if response.status_code == 204:
            session.clear()
            return redirect(url_for('index'))
        else:
            return render_template('deletar_conta.html', nome=nome_usuario, error="Erro ao deletar usuário.")
    
    return render_template('deletar_conta.html', nome=nome_usuario)

# Rota: /trocar_senha
# Descrição: Permite ao usuário trocar sua senha.
# Tipo: Rota
# Histórico: 
@app.route('/trocar_senha', methods=['GET', 'POST'])
def trocar_senha():

    nome_usuario = session.get('nome', 'Sem Nome')
    if not valida_acesso():
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = session.get('email')
        token = session.get('token')
        senha = request.form.get("senha")
        headers = {"x-access-token": token}
        response = requests.patch(f"{API_BASE_URL}{PATCH_USER_ENDPOINT}{email}", json={"senha": senha}, headers=headers)
        if response.status_code == 200:
            session.clear()
            return redirect(url_for('index'))
        else:
            return render_template('trocar_senha.html', nome=nome_usuario, error="Erro ao trocar a senha.")
    
    return render_template('trocar_senha.html', nome=nome_usuario)

# Rota: /pergunta
# Descrição: Exibe a página de perguntas durante a partida, gerenciando as interações do jogador.
# Tipo: Rota
# Histórico: 
@app.route('/pergunta', methods=['GET', 'POST'])
def pergunta():
    
    nome_usuario = session.get('nome', 'Sem Nome')
    email = session.get('email')
    if not valida_acesso():
        return redirect(url_for('index'))

    if request.method == 'GET':
        id_ultimo_jogo = ultimo_jogo(email)
        proxima_rodada(id_ultimo_jogo['id'],email)
        complet_pkm_player = session.get('complet_pkm_player', [])
        complet_pkm_cpu = session.get('complet_pkm_cpu', [])
        id_player_begin = session['player_begin']
        rodada = session['rodada']
        if id_player_begin == 2:
            escolha_IA(complet_pkm_cpu, None)
            atributo_escolhido = session.get('atributo_escolhido')
            atributo_disabled = True
            return render_template('partida.html', pkm_player=complet_pkm_player, pkm_cpu=complet_pkm_cpu,atributo=atributo_escolhido,atributo_disabled=atributo_disabled, nome=nome_usuario, id_rodada=rodada)
        return render_template('partida.html', pkm_player=complet_pkm_player, pkm_cpu=complet_pkm_cpu, nome=nome_usuario, id_rodada=rodada)
    else: 
        token = session.get('token')
        headers = {"x-access-token": token}
        requests.patch(f"{API_BASE_URL}{PATCH_MATCHCLEAR_ENPOINT}", json={"email": email}, headers=headers)
        return redirect(url_for('menu'))  

# Rota: /partida
# Descrição: Gerencia o andamento da partida e as ações do jogador e da IA.
# Tipo: Rota
# Histórico: 
@app.route('/partida', methods=['GET', 'POST'])
def partida():

    nome_usuario = session.get('nome', 'Sem Nome')
    email = session.get('email')
    if not valida_acesso():
        return redirect(url_for('index'))
  
    if request.method == 'GET':

        # Existe Partida Em Aberto?
        id_ultimo_jogo = ultimo_jogo(email)
        if id_ultimo_jogo and 'id' in id_ultimo_jogo and isinstance(id_ultimo_jogo['id'], int) and id_ultimo_jogo['id'] >= 1:
            return render_template('pergunta.html', nome=nome_usuario)
        else:
            # Iniciando Partida
            comprar_cartas() #Função comprar cartas
            grava_partida(session['id_pkm_player'], session['id_pkm_cpu']) #Função gravar partida
            grava_resultado() #Função gravar resultado
            grava_rodada() #Função gravar rodada
            complet_pkm_player = session.get('complet_pkm_player', [])
            complet_pkm_cpu = session.get('complet_pkm_cpu', [])
            id_player_begin = session['player_begin']
            rodada = session['rodada']
            if id_player_begin == 2:
                escolha_IA(complet_pkm_cpu, None)
                atributo_escolhido = session.get('atributo_escolhido')
                atributo_disabled = True
                return render_template('partida.html', pkm_player=complet_pkm_player, pkm_cpu=complet_pkm_cpu,atributo=atributo_escolhido,atributo_disabled=atributo_disabled, nome=nome_usuario, id_rodada=rodada)
            return render_template('partida.html', pkm_player=complet_pkm_player, pkm_cpu=complet_pkm_cpu, nome=nome_usuario, id_rodada=rodada)

    else:
        # Preparando Próxima Rodada
        id_ultimo_jogo = session['id_ultimo_jogo']
        if id_ultimo_jogo == '' or id_ultimo_jogo is None:
            id_partida = session['id_partida']
        else:
            id_partida = session['id_ultimo_jogo']

        proxima_rodada(id_partida, email)
        complet_pkm_cpu = session.get('complet_pkm_cpu', [])
        complet_pkm_player = session.get('complet_pkm_player', [])
        rodada = session['rodada']
        if session.get('rodada', 0) > 6:
            gravar_final()
            historico_partidas()
            resultado_partida = session.get('resultado_partida', {})
            resultado_geral = session.get('resultado_geral', {})
            resultado_partida_V = resultado_partida.get('Player', 0)
            resultado_partida_E = resultado_partida.get('Empate', 0)
            resultado_partida_D = resultado_partida.get('CPU', 0)
            resultado_geral_V = resultado_geral.get('Vitoria', 0)
            resultado_geral_E = resultado_geral.get('Empate', 0)
            resultado_geral_D = resultado_geral.get('Derrota', 0)
            return render_template('resultado.html', resultado_partida_V=resultado_partida_V, 
                                   resultado_partida_E=resultado_partida_E, 
                                   resultado_partida_D=resultado_partida_D, 
                                   resultado_geral_V=resultado_geral_V, 
                                   resultado_geral_E=resultado_geral_E, 
                                   resultado_geral_D=resultado_geral_D)
        
        else:
            if session.get('player_begin') == 2:
                escolha_IA(complet_pkm_cpu, None)
                atributo_escolhido = session.get('atributo_escolhido')
                atributo_disabled = True
                return render_template('partida.html', pkm_player=complet_pkm_player, pkm_cpu=complet_pkm_cpu,atributo=atributo_escolhido,atributo_disabled=atributo_disabled, nome=nome_usuario, id_rodada=rodada)
            else:
                return render_template('partida.html', pkm_player=complet_pkm_player, pkm_cpu=complet_pkm_cpu, nome=nome_usuario, id_rodada=rodada)

# Rota: /resultado_rodada
# Descrição: Exibe os resultado da rodada N da partida.
# Tipo: Rota
# Histórico: 
@app.route('/resultado_rodada', methods=['POST'])
def resultado_rodada():

    if not valida_acesso():
        return redirect(url_for('index'))
    
    # Gravar Rodada
    complet_pkm_cpu = session.get('complet_pkm_cpu', [])
    pokemon_id = int(request.form['pokemon_id'])
    atributo = request.form['atributo']
    rodada = session['rodada']
    player_begin = session['player_begin']

    id_ultimo_jogo = session['id_ultimo_jogo']
    if id_ultimo_jogo == '' or id_ultimo_jogo is None:
        id_partida = session['id_partida']
    else:
        id_partida = session['id_ultimo_jogo']

    if atributo != 'cpu':
        escolha_IA(complet_pkm_cpu, atributo)

    melhor_pokemon = session['melhor_pokemon']
    atributo_escolhido = session['atributo_escolhido']

    if atributo == '' or atributo == 'cpu':
        resultado = batalha(pokemon_id,melhor_pokemon['id'],atributo_escolhido)
        grava_turno(id_partida, resultado, pokemon_id, melhor_pokemon['id'], rodada, player_begin)
    else:
        resultado = batalha(pokemon_id,melhor_pokemon['id'],atributo)
        grava_turno(id_partida, resultado, pokemon_id, melhor_pokemon['id'], rodada, player_begin) 

    complet_pkm_cpu = session.get('complet_pkm_cpu', [])
    complet_pkm_player = session.get('complet_pkm_player', [])

    return render_template('resultado_rodada.html', id_rodada=rodada, pkm_player=complet_pkm_player, pokemon_player=pokemon_id, pkm_cpu=complet_pkm_cpu, pokemon_cpu=melhor_pokemon['id'], atributo=atributo_escolhido)
    

# Rota: /resultado
# Descrição: Exibe os resultados finais da partida.
# Tipo: Rota
# Histórico: 
@app.route('/resultado', methods=['GET'])
def resultado():

    nome_usuario = session.get('nome', 'Sem Nome')
    if not valida_acesso():
        return redirect(url_for('index'))
    return render_template('resultado.html', nome=nome_usuario)

# Rota: /historico
# Descrição: Exibe o histórico geral de partidas do usuário.
# Tipo: Rota
# Histórico: 
@app.route('/historico', methods=['GET'])
def historico():

    nome_usuario = session.get('nome', 'Sem Nome')
    if not valida_acesso():
        return redirect(url_for('index'))

    historico_partidas()
    resultado_geral = session.get('resultado_geral', {})
    resultado_geral_V = resultado_geral.get('Vitoria', 0)
    resultado_geral_E = resultado_geral.get('Empate', 0)
    resultado_geral_D = resultado_geral.get('Derrota', 0)

    return render_template('historico.html', nome=nome_usuario, 
                            resultado_geral_V=resultado_geral_V, 
                            resultado_geral_E=resultado_geral_E, 
                            resultado_geral_D=resultado_geral_D)

# Rota: /menu
# Descrição: Exibe o menu principal após o login.
# Tipo: Rota
# Histórico: 
@app.route('/menu')
def menu():

    nome_usuario = session.get('nome', 'Sem Nome')
    if not valida_acesso():
        return redirect(url_for('index'))
    
    return render_template('menu.html', nome=nome_usuario)

# Rota: /sair
# Descrição: Finaliza a sessão do usuário e o redireciona para a página inicial.
# Tipo: Rota
# Histórico: 
@app.route('/sair', methods=['GET'])
def sair():

    if not valida_acesso():
        return redirect(url_for('index'))
    
    session.clear()

    return redirect(url_for('index'))
    
if __name__ == '__main__':
    app.run(debug=True)
