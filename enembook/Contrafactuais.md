# Contrafactuais
Pensando sobre a confiabiliade da nota ENEM, é interessante considerar os efeitos sobre a nota de pequenas mudanças aparente inocentes, por exemplo no procedimento de como a nota é calculado, ou se o candidato acerta uma única questão a mais ou a menos. Uma motivação disso é mostrar que a nota atribuída a cada candidato deve ser interpretado e não simplesmente tido como verdade absoluta. Queremos chacoalhar um pouco na suposta objetividade da nota, a ideia errônea que a prova ENEM reflete fielmente e sem incerteza a aptidão de um candidato para cursar o ensino superior.

Como já afirmamos, a confiabilidade da nota ENEM é uma condição necessária, mas não suficiente para o ENEM ser uma medida válida. Neste capítulo restringimos nossa análise aos possíveis fatores associados com a confiabilidade ou *incerteza* da nota ENEM.

Uma maneira de fazer isso é criar uma série de contrafactuais. Por exemplo, podemos imaginar modifaçoes (razoáveis, pequenas) no procedimento de cálculo das notas e estudar como a nota muda. Ou, podemos imaginar 

Ou seja, vamos fazer uma espécie de propagação de incerteza, na linguagem de físicos: 

$$ \text{Nota ENEM} = f(\text{padrão de respostas},\text{parâmetros IRT},...) = f(\vec{x})$$
$$ \Delta f \approx \frac{\partial f}{\partial x} \Delta x$$



## Determinação da nota
A nota dos participantes ENEM é calculado pelo INEP a partir dos padrões de respostas às questões das provas, com certas suposições:

* É usado um modelo IRT do tipo 3PL 
* Os parâmetros a, b e c (discriminação, dificuldade e chute, respectivamente) do modelo são calibrados para cada item previamente, por métodos de *linking* que coloquem novas itens na escala ENEM
* A estimativa do *score* na escala ENEM usa o método EAP ("Expected a posteriori")

## 



