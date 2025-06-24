import numpy as np

# Definimos um pequeno valor de tolerância para comparações de ponto flutuante.
# Isso é crucial para evitar erros devido à forma como os números de ponto flutuante são representados.
EPSILON = 1e-9 

class Simplex:
    def __init__(self):
        self.tableau = None
        self.num_var = 0  # Número de variáveis de decisão originais (x1, x2, ...)
        self.num_rest = 0 # Número de restrições
        self.base = []    # Lista de índices das variáveis básicas
        self.non_base = []# Lista de índices das variáveis não básicas
        self.optimal = False           # Flag para indicar se a solução ótima foi encontrada
        self.unbounded = False         # Flag para indicar se o problema é ilimitado
        self.multiple_solutions = False# Flag para indicar se existem múltiplas soluções ótimas
        self.num_slack_surplus_artificial = 0 # Adicionado: para armazenar o número total de variáveis auxiliares

    def load_problem(self, filename):
        #Carrega o problema de Programação Linear de um arquivo de texto.
        
        with open(filename, 'r') as file:
            # Lê o número de variáveis de decisão e restrições
            self.num_var, self.num_rest = map(int, file.readline().split())
            
            # Lê os coeficientes da função objetivo
            c = list(map(float, file.readline().split()))
            
            # Lê os coeficientes das restrições (matriz A), os tipos de restrição e os lados direitos (vetor b)
            A = []
            b = []
            types = []
            for _ in range(self.num_rest):
                line = file.readline().split()
                A_row = list(map(float, line[:-2])) # Coeficientes de A
                types.append(line[-2])              # Tipo de restrição ('<=', '>=', '=')
                b.append(float(line[-1]))           # Lado direito (b)
                A.append(A_row)
            
            # Converte as listas para arrays NumPy para operações eficientes
            A = np.array(A)
            b = np.array(b)
            c = np.array(c)
            
            # Cria o tableau inicial com base nos dados carregados
            self._create_initial_tableau(A, b, c, types)
    
    def _create_initial_tableau(self, A, b, c, types):
      
        # Calcular o número total de variáveis auxiliares (folga/excesso/artificial)
        # Para esta versão simplificada, apenas folga/excesso são consideradas.
        self.num_slack_surplus_artificial = 0 # Agora é um atributo da instância
        for t in types:
            if t == '<=' or t == '>=':
                self.num_slack_surplus_artificial += 1
           
       
        self.tableau = np.zeros((self.num_rest + 1, self.num_var + self.num_slack_surplus_artificial + 1))
        
        # Preenche a primeira linha (linha 0) com os coeficientes da função objetivo.
        # Eles são negados porque o Simplex busca maximizar (ou minimizar o negativo).
        self.tableau[0, :self.num_var] = -c 
        
        # Preenche as linhas das restrições (linhas 1 a num_rest)
        current_aux_var_col_idx = self.num_var # Índice da coluna para a próxima variável auxiliar
        self.base = [] # Reinicia a lista de variáveis básicas

        for i in range(self.num_rest):
            # Copia os coeficientes das variáveis de decisão
            self.tableau[i + 1, :self.num_var] = A[i] 
            
            if types[i] == '<=':
                # Adiciona uma variável de folga com coeficiente +1
                self.tableau[i + 1, current_aux_var_col_idx] = 1 
                # A variável de folga torna-se uma variável básica na base inicial
                self.base.append(current_aux_var_col_idx) 
                current_aux_var_col_idx += 1
            elif types[i] == '>=':
                # Adiciona uma variável de excesso com coeficiente -1
                self.tableau[i + 1, current_aux_var_col_idx] = -1
               
                current_aux_var_col_idx += 1
            # elif types[i] == '=':
            #     # Para restrições '=', apenas uma variável artificial seria adicionada
            #     # e se tornaria básica. Isso também exigiria o Método de Duas Fases/Big M.
            #     pass
            
            # Adiciona o valor do lado direito da restrição
            self.tableau[i + 1, -1] = b[i] 
        
        # Define as variáveis não básicas iniciais: todas as variáveis de decisão originais
        # mais quaisquer variáveis auxiliares que não se tornaram básicas.
        all_variables_indices = set(range(self.num_var + self.num_slack_surplus_artificial)) # Usa o atributo da instância
        self.non_base = sorted(list(all_variables_indices - set(self.base)))
    
    def solve(self):
        
        #Executa o método Simplex para encontrar a solução ótima.
        iteration = 0
        max_iterations = 1000  # Limite para prevenir loops infinitos em problemas degenerados ou cíclicos
        
        while not self.optimal and not self.unbounded and iteration < max_iterations:
            iteration += 1
            
            # 1. Teste de Otimalidade:
            # Se todos os coeficientes na linha da função objetivo (exceto o RHS) são não negativos,
            # a solução atual é ótima. Usamos EPSILON para comparações de ponto flutuante.
            if all(x >= -EPSILON for x in self.tableau[0, :-1]):
                self.optimal = True
                # Se a solução é ótima, verifica se há múltiplas soluções
                self._check_multiple_solutions()
                break # Sai do loop principal
            
            # 2. Seleção da Variável de Entrada (Coluna Pivô):
            # Escolhe a coluna com o menor (mais negativo) coeficiente na linha da função objetivo.
            # A função np.argmin retorna o índice do menor valor.
            entering_col_idx = np.argmin(self.tableau[0, :-1])
            
            # 3. Teste de Ilimitabilidade:
            # Se todos os coeficientes na coluna da variável de entrada (abaixo da linha da FO)
            # são menores ou iguais a zero, o problema é ilimitado.
            # Ou seja, podemos aumentar a variável de entrada indefinidamente sem violar as restrições.
            if all(self.tableau[i, entering_col_idx] <= EPSILON for i in range(1, self.num_rest + 1)):
                self.unbounded = True
                break # Sai do loop principal
            
            # 4. Seleção da Variável de Saída (Linha Pivô) - Teste da Razão Mínima:
            # Calcula as razões entre o lado direito (RHS) e os coeficientes positivos da coluna de entrada.
            # A linha com a menor razão positiva determina qual variável básica sairá da base.
            ratios = []
            for i in range(1, self.num_rest + 1): # Começa da linha 1 (primeira restrição)
                pivot_col_val = self.tableau[i, entering_col_idx]
                if pivot_col_val > EPSILON: # Apenas divisões por valores positivos
                    ratios.append(self.tableau[i, -1] / pivot_col_val)
                else:
                    ratios.append(float('inf')) # Ignora divisões por zero ou negativos
            
            # Se todas as razões são infinitas, significa que não há variável para sair,
            # o que já deveria ter sido pego pelo teste de ilimitabilidade.
            if all(r == float('inf') for r in ratios):
                self.unbounded = True 
                break

            # Encontra o índice da linha com a menor razão positiva.
            # Adicionamos +1 porque as razões foram calculadas para as linhas de 1 a num_rest.
            leaving_row_idx = np.argmin(ratios) + 1 
            
            # 5. Atualiza a Base:
            # A variável que estava na base na linha `leaving_row_idx` é substituída pela
            # variável que está entrando (com o índice `entering_col_idx`).
            # O índice na lista `self.base` corresponde à linha da restrição (i.e., `leaving_row_idx - 1`).
            self.base[leaving_row_idx - 1] = entering_col_idx
            
            # 6. Atualiza as Variáveis Não Básicas:
            # Recalcula a lista de variáveis não básicas para garantir que esteja consistente.
            all_variables_indices = set(range(self.num_var + self.num_slack_surplus_artificial)) # Usa o atributo da instância
            self.non_base = sorted(list(all_variables_indices - set(self.base)))
            
            # 7. Operação de Pivoteamento:
            # Transforma o tableau para que a nova variável de entrada se torne básica
            # e a variável de saída se torne não básica.
            pivot_element = self.tableau[leaving_row_idx, entering_col_idx]
            
            # Normaliza a linha do pivô (divide todos os elementos da linha pelo elemento pivô)
            self.tableau[leaving_row_idx, :] /= pivot_element
            
            # Zera os outros elementos na coluna do pivô
            for i in range(self.num_rest + 1): # Itera por todas as linhas (incluindo a função objetivo)
                if i != leaving_row_idx: # Não opera na linha do pivô
                    self.tableau[i, :] -= self.tableau[i, entering_col_idx] * self.tableau[leaving_row_idx, :]
    
    def _check_multiple_solutions(self):
        for j in self.non_base:
            if abs(self.tableau[0, j]) < EPSILON: # Se o coeficiente for (quase) zero
                self.multiple_solutions = True
                break
        
    def get_solution(self):
        if self.unbounded:
            return "Problema ilimitado"
        
        if self.optimal:
            solution = np.zeros(self.num_var) # Inicializa as variáveis de decisão com zero
            
            # Para cada linha de restrição (1 a num_rest), identifica a variável básica
            # e atribui o valor do lado direito (RHS) a essa variável.
            for i in range(self.num_rest): # Itera de 0 a num_rest-1, que corresponde às linhas 1 a num_rest do tableau
                basic_var_idx = self.base[i] # O índice da variável básica na linha 'i' da lista 'self.base'
                if basic_var_idx < self.num_var: # Se for uma das variáveis de decisão originais (x1, x2, ...)
                    solution[basic_var_idx] = self.tableau[i + 1, -1] # O valor é o RHS da linha correspondente no tableau
            
            return {
                'solution': solution,          # Valores das variáveis de decisão ótimas
                'optimal_value': self.tableau[0, -1], # Valor ótimo da função objetivo
                'multiple_solutions': self.multiple_solutions, # Se há múltiplas soluções
                'base': self.base              # Variáveis básicas finais
            }
        else:
            return "Solução não encontrada ou problema ainda não resolvido. Verifique o limite de iterações ou se o problema é infactível."
    
    def print_tableau(self):
        print("Tableau:")
        print(np.round(self.tableau, 4)) # Arredonda para 4 casas decimais
        print(f"Variáveis básicas (índices): {self.base}")
        print(f"Variáveis não básicas (índices): {self.non_base}")
        print("-" * 30)


# Exemplo de uso
if __name__ == "__main__":
    
    with open("problema.txt", "w") as f:
        f.write("2 2\n")         # 2 variáveis, 2 restrições
        f.write("3 2\n")         # Coeficientes da função objetivo (c)
        f.write("2 1 <= 10\n")   # Restrição 1: 2x1 + x2 <= 10
        f.write("1 3 <= 15\n")   # Restrição 2: x1 + 3x2 <= 15


    simplex = Simplex()
    
    # Carrega o problema do arquivo
    # Altere para "problema_ilimitado.txt" ou "problema_multiplas.txt" para testar
    simplex.load_problem("problema.txt") 
    
    # Imprime o tableau inicial
    simplex.print_tableau() 
    
    # Executa o método Simplex
    simplex.solve()
    
    # Obtém e imprime a solução
    solution = simplex.get_solution()
    
    if isinstance(solution, str):
        print("\n" + solution) # Se for uma mensagem de erro (ilimitado, etc.)
    else:
        print("\nSolução encontrada:")
        print(f"Valor ótimo: {solution['optimal_value']:.4f}") # Formata para 4 casas decimais
        print(f"Variáveis (x1, x2, ...): {solution['solution']}")
        
        if solution['multiple_solutions']:
            print("Existem múltiplas soluções ótimas.")
        
        print(f"Variáveis básicas finais (índices): {solution['base']}")
        simplex.print_tableau() # Imprime o tableau final
