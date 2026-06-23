# * [RESUMO] → Views do app core.
#              Contém as views globais do sistema — login, logout e homepage.

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# ================================================
# LOGIN
# ================================================

def view_login(request):
    # * [EXPLICAÇÃO] → Se o usuário já está autenticado, redireciona
    #                  direto para a homepage — sem mostrar o login.
    if request.user.is_authenticated:
        return redirect('/')

    erro = None

    if request.method == 'POST':
        # * [EXPLICAÇÃO] → Pega os dados do formulário enviado pelo usuário.
        usuario = request.POST.get('username')
        senha   = request.POST.get('password')

        # * [EXPLICAÇÃO] → O authenticate() verifica se o usuário e senha
        #                  existem no banco. Retorna o objeto User se correto,
        #                  ou None se incorreto.
        user = authenticate(request, username=usuario, password=senha)

        if user is not None:
            # * [EXPLICAÇÃO] → O login() inicia a sessão do usuário —
            #                  salva os dados de autenticação no cookie.
            login(request, user)
            return redirect('/')
        else:
            # * [EXPLICAÇÃO] → Se authenticate() retornou None, as credenciais
            #                  estão erradas. Passamos o erro para o template.
            erro = 'Usuário ou senha incorretos.'

    return render(request, 'pagina_login/estrutura_login.html', {'erro': erro})


# ================================================
# LOGOUT
# ================================================

def view_logout(request):
    # * [EXPLICAÇÃO] → O logout() encerra a sessão do usuário —
    #                  remove os dados de autenticação do cookie.
    logout(request)
    return redirect('/login/')