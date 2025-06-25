**Estratégia de Testes para o Código Simplex**
Para testar seu código de forma eficaz, você deve criar arquivos problema.txt para cada uma das seguintes categorias de problemas:

**1. Problemas com Solução Ótima Única (Padrão)**
São os casos mais comuns, onde o algoritmo deve convergir para uma única solução ótima e finita.

Características: Restrições do tipo "
le", lados direitos (RHS) positivos, e uma solução clara.
Exemplo problema_otimo.txt:
2 2
3 2
2 1 <= 10
1 3 <= 15
Função Objetivo: Max 3x_1+2x_2
Restrições:
2x_1+x_2
le10
x_1+3x_2
le15
Valores Esperados (aproximados): x_1
approx3.46, x_2
approx3.85, Ótimo
approx18.08

**2. Problemas Ilimitados (Unbounded)**
Ocorre quando a função objetivo pode ser aumentada (para maximização) ou diminuída (para minimização) indefinidamente sem violar nenhuma restrição. Seu código deve identificar isso com self.unbounded = True.

Características: Pelo menos uma variável pode aumentar indefinidamente. No tableau, isso se manifesta quando a coluna da variável que entra na base tem todos os elementos (abaixo da linha da FO) negativos ou zero.
Exemplo problema_ilimitado.txt:
1 1
1
-1 <= -1
Função Objetivo: Max x_1
Restrição: −x_1
le−1 (equivalente a x_1
ge1)
Nesse caso, x_1 pode crescer infinitamente.

**3. Problemas Infactíveis (Infeasible)**
Ocorre quando não há nenhuma solução que satisfaça todas as restrições simultaneamente. Seu código atual, como mencionado, não tem um tratamento robusto para detectar infactibilidade diretamente para todos os casos (especialmente com restrições >=' ou '='). Geralmente, isso é detectado no Método de Duas Fases ou Big M quando uma variável artificial permanece básica com valor positivo na solução ótima da Fase 1.

Características: As restrições se contradizem.
Exemplo (conceptual, pois seu código não detectará explicitamente sem Duas Fases):
1 2
1
1 <= 5
1 >= 10
Função Objetivo: Max x_1
Restrições:
x_1
le5
x_1
ge10
É impossível para x_1 ser menor ou igual a 5 E maior ou igual a 10 ao mesmo tempo.

**4. Problemas com Múltiplas Soluções Ótimas**
Ocorre quando existem múltiplos pontos que fornecem o mesmo valor ótimo para a função objetivo. Seu código deve identificar isso com self.multiple_solutions = True.

Características: Na solução ótima, uma ou mais variáveis não básicas têm um coeficiente de zero na linha da função objetivo.
Exemplo problema_multiplas.txt:
2 2
2 4
1 2 <= 8
1 1 <= 6
Função Objetivo: Max 2x_1+4x_2
Restrições:
x_1+2x_2
le8
x_1+x_2
le6
A linha da função objetivo 2x_1+4x_2 é paralela a x_1+2x_2=8, indicando a possibilidade de múltiplas soluções.

**5. Problemas com Degeneração**
A degeneração ocorre quando uma variável básica tem um valor de zero. Isso pode levar a iterações do Simplex que não melhoram o valor da função objetivo, e em casos raros, a um ciclo (cycling). Seu código pode não ter uma estratégia para evitar ciclos, mas deve ser capaz de lidar com a degeneração em si.

Características: Na tabela Simplex, o RHS de uma linha básica é zero.
Exemplo problema_degenerado.txt:
2 2
3 2
2 1 <= 0
1 3 <= 15
Função Objetivo: Max 3x_1+2x_2
Restrições:
2x_1+x_2
le0 (implica x_1=0,x_2=0 se x_1,x_2
ge0)
x_1+3x_2
le15

**6. Problemas com Diferentes Tipos de Restrições (e as Limitações do seu Código)**
É crucial testar com restrições `>=' e '='. No entanto, lembre-se da limitação do seu código: ele não implementa o Método de Duas Fases ou Big M, que são necessários para garantir uma base factível inicial para esses tipos de restrições.

Como seu código atual se comporta (limitação):

Para A[i] >= b[i]: Adiciona uma variável de excesso com coeficiente -1. No tableau inicial, isso resulta em um -1 na coluna da variável de excesso e um b[i] no RHS. Se b[i] for positivo, a solução básica inicial para essa variável será negativa (infactível). O Simplex padrão não consegue resolver isso sem uma fase auxiliar.
Para A[i] = b[i]: Seu código não tem lógica para isso.
Exemplo problema_ge.txt (Para observar o comportamento atual, mas ciente da limitação):

2 2
3 2
2 1 >= 5
1 3 <= 15
Função Objetivo: Max $3x_1 + 2x_2$
Restrições:
$2x_1 + x_2 \ge 5$ (isso provavelmente levará a um problema de factibilidade inicial no seu código)
$x_1 + 3x_2 \le 15$

**7. Problemas de Diferentes Tamanhos**
Teste com um número pequeno de variáveis/restrições (2x2, 3x3), e também com problemas maiores (10x10, 20x20) para verificar o desempenho e a estabilidade numérica.

Como Implementar os Testes
Crie os Arquivos problema.txt: Salve os exemplos acima em arquivos separados (ex: problema_otimo.txt, problema_ilimitado.txt, etc.).

Modifique o Bloco if __name__ == "__main__"::
Você pode criar um loop ou uma sequência para testar cada arquivo e imprimir os resultados.
if __name__ == "__main__":
    test_problems = {
        "problema_otimo.txt": "Solução ótima única esperada",
        "problema_ilimitado.txt": "Problema ilimitado esperado",
        "problema_multiplas.txt": "Múltiplas soluções ótimas esperadas",
        "problema_degenerado.txt": "Problema degenerado esperado",
        "problema_ge.txt": "Problema com restrição >= (verificar comportamento, pode ser infactível com simplex padrão)"
    }

    # Crie os arquivos de teste programaticamente para garantir que existam
    with open("problema_otimo.txt", "w") as f:
        f.write("2 2\n3 2\n2 1 <= 10\n1 3 <= 15\n")
    with open("problema_ilimitado.txt", "w") as f:
        f.write("1 1\n1\n-1 <= -1\n")
    with open("problema_multiplas.txt", "w") as f:
        f.write("2 2\n2 4\n1 2 <= 8\n1 1 <= 6\n")
    with open("problema_degenerado.txt", "w") as f:
        f.write("2 2\n3 2\n2 1 <= 0\n1 3 <= 15\n")
    with open("problema_ge.txt", "w") as f:
        f.write("2 2\n3 2\n2 1 >= 5\n1 3 <= 15\n")


    for filename, description in test_problems.items():
        print(f"\n--- Testando: {filename} ({description}) ---")
        simplex = Simplex()
        try:
            simplex.load_problem(filename)
            print("Tableau Inicial:")
            simplex.print_tableau()
            simplex.solve()

            solution = simplex.get_solution()

            if isinstance(solution, str):
                print(solution)
            else:
                print("\nSolução Encontrada:")
                print(f"Valor ótimo: {solution['optimal_value']:.4f}")
                print(f"Variáveis (x1, x2, ...): {solution['solution']}")

                if solution['multiple_solutions']:
                    print("Existem múltiplas soluções ótimas.")

                print(f"Variáveis básicas finais (índices): {solution['base']}")

            print("Tableau Final:")
            simplex.print_tableau()

        except Exception as e:
            print(f"Ocorreu um erro ao processar {filename}: {e}")
        print("-" * 50)
