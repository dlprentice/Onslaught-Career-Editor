/* address: 0x005738e0 */
/* name: CTexture__EraseNodeFromTree */
/* signature: void __thiscall CTexture__EraseNodeFromTree(void * this, int param_1, void * param_2, void * param_3) */


void __thiscall CTexture__EraseNodeFromTree(void *this,int param_1,void *param_2,void *param_3)

{
  int iVar1;
  int *piVar2;
  int *piVar3;
  undefined4 *puVar4;
  int *piVar5;
  void *pvVar6;
  int *piVar7;
  undefined4 *puVar8;
  int *piVar9;
  undefined4 *puVar10;
  int *local_4;

  pvVar6 = param_2;
  CTexture__TreeIteratorPrev(&param_2);
  piVar7 = *(int **)pvVar6;
  local_4 = pvVar6;
  if (piVar7 == DAT_009d0c44) {
    piVar9 = *(int **)((int)pvVar6 + 8);
  }
  else {
    piVar2 = *(int **)((int)pvVar6 + 8);
    piVar9 = piVar7;
    if (piVar2 != DAT_009d0c44) {
      for (piVar9 = (int *)*piVar2; piVar9 != DAT_009d0c44; piVar9 = (int *)*piVar9) {
        piVar2 = piVar9;
      }
      piVar9 = (int *)piVar2[2];
      local_4 = piVar2;
      if (piVar2 != pvVar6) {
        piVar7[1] = (int)piVar2;
        *piVar2 = *(int *)pvVar6;
        if (piVar2 == *(int **)((int)pvVar6 + 8)) {
          piVar9[1] = (int)piVar2;
        }
        else {
          piVar9[1] = piVar2[1];
          *(int **)piVar2[1] = piVar9;
          piVar2[2] = *(int *)((int)pvVar6 + 8);
          *(int **)(*(int *)((int)pvVar6 + 8) + 4) = piVar2;
        }
        if (*(void **)(*(int *)((int)this + 4) + 4) == pvVar6) {
          *(int **)(*(int *)((int)this + 4) + 4) = piVar2;
        }
        else {
          piVar7 = *(int **)((int)pvVar6 + 4);
          if ((void *)*piVar7 == pvVar6) {
            *piVar7 = (int)piVar2;
          }
          else {
            piVar7[2] = (int)piVar2;
          }
        }
        local_4 = pvVar6;
        piVar2[1] = *(int *)((int)pvVar6 + 4);
        iVar1 = piVar2[4];
        piVar2[4] = *(int *)((int)pvVar6 + 0x10);
        *(int *)((int)pvVar6 + 0x10) = iVar1;
        goto LAB_00573a0f;
      }
    }
  }
  piVar9[1] = local_4[1];
  if (*(void **)(*(int *)((int)this + 4) + 4) == pvVar6) {
    *(int **)(*(int *)((int)this + 4) + 4) = piVar9;
  }
  else {
    piVar7 = *(int **)((int)pvVar6 + 4);
    if ((void *)*piVar7 == pvVar6) {
      *piVar7 = (int)piVar9;
    }
    else {
      piVar7[2] = (int)piVar9;
    }
  }
  piVar7 = *(int **)((int)this + 4);
  if ((void *)*piVar7 == pvVar6) {
    if (*(int **)((int)pvVar6 + 8) == DAT_009d0c44) {
      *piVar7 = *(int *)((int)pvVar6 + 4);
    }
    else {
      piVar3 = (int *)*piVar9;
      piVar2 = piVar9;
      while (piVar5 = piVar3, piVar5 != DAT_009d0c44) {
        piVar2 = piVar5;
        piVar3 = (int *)*piVar5;
      }
      *piVar7 = (int)piVar2;
    }
  }
  if (*(void **)(*(int *)((int)this + 4) + 8) == pvVar6) {
    if (*(int **)pvVar6 == DAT_009d0c44) {
      piVar7 = *(int **)((int)pvVar6 + 4);
    }
    else {
      piVar2 = (int *)piVar9[2];
      piVar7 = piVar9;
      while (piVar3 = piVar2, piVar3 != DAT_009d0c44) {
        piVar7 = piVar3;
        piVar2 = (int *)piVar3[2];
      }
    }
    *(int **)(*(int *)((int)this + 4) + 8) = piVar7;
  }
LAB_00573a0f:
  if (local_4[4] == 1) {
    if (piVar9 != *(int **)(*(int *)((int)this + 4) + 4)) {
      do {
        if (piVar9[4] != 1) break;
        piVar7 = *(int **)piVar9[1];
        if (piVar9 == piVar7) {
          piVar7 = (int *)((undefined4 *)piVar9[1])[2];
          if (piVar7[4] == 0) {
            piVar7[4] = 1;
            *(undefined4 *)(piVar9[1] + 0x10) = 0;
            iVar1 = piVar9[1];
            piVar7 = *(int **)(iVar1 + 8);
            *(int *)(iVar1 + 8) = *piVar7;
            if ((int *)*piVar7 != DAT_009d0c44) {
              ((int *)*piVar7)[1] = iVar1;
            }
            piVar7[1] = *(int *)(iVar1 + 4);
            if (iVar1 == *(int *)(*(int *)((int)this + 4) + 4)) {
              *(int **)(*(int *)((int)this + 4) + 4) = piVar7;
            }
            else {
              piVar2 = *(int **)(iVar1 + 4);
              if (iVar1 == *piVar2) {
                *piVar2 = (int)piVar7;
              }
              else {
                piVar2[2] = (int)piVar7;
              }
            }
            *piVar7 = iVar1;
            *(int **)(iVar1 + 4) = piVar7;
            piVar7 = *(int **)(piVar9[1] + 8);
          }
          if ((*(int *)(*piVar7 + 0x10) != 1) || (*(int *)(piVar7[2] + 0x10) != 1)) {
            if (*(int *)(piVar7[2] + 0x10) == 1) {
              *(undefined4 *)(*piVar7 + 0x10) = 1;
              iVar1 = *piVar7;
              piVar7[4] = 0;
              *piVar7 = *(int *)(iVar1 + 8);
              if (*(int **)(iVar1 + 8) != DAT_009d0c44) {
                (*(int **)(iVar1 + 8))[1] = (int)piVar7;
              }
              *(int *)(iVar1 + 4) = piVar7[1];
              if (piVar7 == *(int **)(*(int *)((int)this + 4) + 4)) {
                *(int *)(*(int *)((int)this + 4) + 4) = iVar1;
              }
              else {
                piVar2 = (int *)piVar7[1];
                if (piVar7 == (int *)piVar2[2]) {
                  piVar2[2] = iVar1;
                }
                else {
                  *piVar2 = iVar1;
                }
              }
              *(int **)(iVar1 + 8) = piVar7;
              piVar7[1] = iVar1;
              piVar7 = *(int **)(piVar9[1] + 8);
            }
            piVar7[4] = *(int *)(piVar9[1] + 0x10);
            *(undefined4 *)(piVar9[1] + 0x10) = 1;
            *(undefined4 *)(piVar7[2] + 0x10) = 1;
            puVar8 = (undefined4 *)piVar9[1];
            puVar10 = (undefined4 *)puVar8[2];
            puVar8[2] = *puVar10;
            if ((int *)*puVar10 != DAT_009d0c44) {
              ((int *)*puVar10)[1] = (int)puVar8;
            }
            puVar10[1] = puVar8[1];
            if (puVar8 == *(undefined4 **)(*(int *)((int)this + 4) + 4)) {
              *(undefined4 **)(*(int *)((int)this + 4) + 4) = puVar10;
              *puVar10 = puVar8;
            }
            else {
              piVar7 = (int *)puVar8[1];
              if (puVar8 == (undefined4 *)*piVar7) {
                *piVar7 = (int)puVar10;
                *puVar10 = puVar8;
              }
              else {
                piVar7[2] = (int)puVar10;
                *puVar10 = puVar8;
              }
            }
LAB_00573c8c:
            puVar8[1] = puVar10;
            break;
          }
        }
        else {
          if (piVar7[4] == 0) {
            piVar7[4] = 1;
            *(undefined4 *)(piVar9[1] + 0x10) = 0;
            piVar7 = (int *)piVar9[1];
            iVar1 = *piVar7;
            *piVar7 = *(int *)(iVar1 + 8);
            if (*(int **)(iVar1 + 8) != DAT_009d0c44) {
              (*(int **)(iVar1 + 8))[1] = (int)piVar7;
            }
            *(int *)(iVar1 + 4) = piVar7[1];
            if (piVar7 == *(int **)(*(int *)((int)this + 4) + 4)) {
              *(int *)(*(int *)((int)this + 4) + 4) = iVar1;
            }
            else {
              piVar2 = (int *)piVar7[1];
              if (piVar7 == (int *)piVar2[2]) {
                piVar2[2] = iVar1;
              }
              else {
                *piVar2 = iVar1;
              }
            }
            *(int **)(iVar1 + 8) = piVar7;
            piVar7[1] = iVar1;
            piVar7 = *(int **)piVar9[1];
          }
          if ((*(int *)(piVar7[2] + 0x10) != 1) || (*(int *)(*piVar7 + 0x10) != 1)) {
            if (*(int *)(*piVar7 + 0x10) == 1) {
              *(undefined4 *)(piVar7[2] + 0x10) = 1;
              piVar2 = (int *)piVar7[2];
              piVar7[4] = 0;
              piVar7[2] = *piVar2;
              if ((int *)*piVar2 != DAT_009d0c44) {
                ((int *)*piVar2)[1] = (int)piVar7;
              }
              piVar2[1] = piVar7[1];
              if (piVar7 == *(int **)(*(int *)((int)this + 4) + 4)) {
                *(int **)(*(int *)((int)this + 4) + 4) = piVar2;
              }
              else {
                piVar3 = (int *)piVar7[1];
                if (piVar7 == (int *)*piVar3) {
                  *piVar3 = (int)piVar2;
                }
                else {
                  piVar3[2] = (int)piVar2;
                }
              }
              *piVar2 = (int)piVar7;
              piVar7[1] = (int)piVar2;
              piVar7 = *(int **)piVar9[1];
            }
            piVar7[4] = *(int *)(piVar9[1] + 0x10);
            *(undefined4 *)(piVar9[1] + 0x10) = 1;
            *(undefined4 *)(*piVar7 + 0x10) = 1;
            puVar8 = (undefined4 *)piVar9[1];
            puVar10 = (undefined4 *)*puVar8;
            *puVar8 = puVar10[2];
            if ((int *)puVar10[2] != DAT_009d0c44) {
              ((int *)puVar10[2])[1] = (int)puVar8;
            }
            puVar10[1] = puVar8[1];
            if (puVar8 == *(undefined4 **)(*(int *)((int)this + 4) + 4)) {
              *(undefined4 **)(*(int *)((int)this + 4) + 4) = puVar10;
            }
            else {
              puVar4 = (undefined4 *)puVar8[1];
              if (puVar8 == (undefined4 *)puVar4[2]) {
                puVar4[2] = puVar10;
              }
              else {
                *puVar4 = puVar10;
              }
            }
            puVar10[2] = puVar8;
            goto LAB_00573c8c;
          }
        }
        piVar7[4] = 0;
        piVar9 = (int *)piVar9[1];
      } while (piVar9 != *(int **)(*(int *)((int)this + 4) + 4));
    }
    piVar9[4] = 1;
  }
  OID__FreeObject_Callback(local_4);
  *(int *)((int)this + 0xc) = *(int *)((int)this + 0xc) + -1;
  *(void **)param_1 = param_2;
  return;
}
