# exp-007: Group-Aware CV Diagnostic

Compare ordinary stratified CV against group-aware CV using `PassengerId`
groups. This diagnoses whether the local score may be optimistic when passengers
from the same group are split across folds.
