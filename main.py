import Simplex as Sim

if __name__ == "__main__":
    
    # with open("problema.txt", "w") as f:
    #     f.write("2 2\n")         # 2 variáveis, 2 restrições
    #     f.write("3 2\n")         # Coeficientes da função objetivo (c)
    #     f.write("2 1 <= 10\n")   # Restrição 1: 2x1 + x2 <= 10
    #     f.write("1 3 <= 15\n")   # Restrição 2: x1 + 3x2 <= 15


    simplex = Sim.Simplex()
    
    simplex.load_problem("problema.txt") 
    
    simplex.print_tableau() 
    
    simplex.solve()
    
    solution = simplex.get_solution()
    
    if isinstance(solution, str):
        print("\n" + solution)
    else:
        print("\nSolução encontrada:")
        print(f"Valor ótimo: {solution['optimal_value']:.4f}")
        print(f"Variáveis (x1, x2, ...): {solution['solution']}")
        
        if solution['multiple_solutions']:
            print("Existem múltiplas soluções ótimas.")
        
        print(f"Variáveis básicas finais (índices): {solution['base']}")
        simplex.print_tableau()
