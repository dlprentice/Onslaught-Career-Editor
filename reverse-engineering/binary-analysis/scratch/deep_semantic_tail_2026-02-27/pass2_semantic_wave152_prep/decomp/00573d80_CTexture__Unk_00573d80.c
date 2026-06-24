/* address: 0x00573d80 */
/* name: CTexture__Unk_00573d80 */
/* signature: int CTexture__Unk_00573d80(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__Unk_00573d80(void)

{
  int iVar1;
  int *piVar2;
  int *extraout_EAX;
  int *piVar3;
  int in_ECX;
  int *piVar4;
  int *piVar5;
  undefined4 *in_stack_00000004;
  int in_stack_00000008;
  int *in_stack_0000000c;
  uint *in_stack_00000010;

  CFastVB__Helper_00426fd0(0x14);
  extraout_EAX[1] = (int)in_stack_0000000c;
  extraout_EAX[4] = 0;
  *extraout_EAX = DAT_009d0c44;
  extraout_EAX[2] = DAT_009d0c44;
  CFastVB__Helper_00574230(extraout_EAX + 3,in_stack_00000010);
  *(int *)(in_ECX + 0xc) = *(int *)(in_ECX + 0xc) + 1;
  if (((in_stack_0000000c == *(int **)(in_ECX + 4)) || (in_stack_00000008 != DAT_009d0c44)) ||
     (*in_stack_00000010 < (uint)in_stack_0000000c[3])) {
    *in_stack_0000000c = (int)extraout_EAX;
    piVar3 = *(int **)(in_ECX + 4);
    if (in_stack_0000000c == piVar3) {
      piVar3[1] = (int)extraout_EAX;
      *(int **)(*(int *)(in_ECX + 4) + 8) = extraout_EAX;
    }
    else if (in_stack_0000000c == (int *)*piVar3) {
      *piVar3 = (int)extraout_EAX;
    }
  }
  else {
    in_stack_0000000c[2] = (int)extraout_EAX;
    if (in_stack_0000000c == *(int **)(*(int *)(in_ECX + 4) + 8)) {
      *(int **)(*(int *)(in_ECX + 4) + 8) = extraout_EAX;
    }
  }
  piVar3 = extraout_EAX;
  if (extraout_EAX != *(int **)(*(int *)(in_ECX + 4) + 4)) {
    do {
      piVar4 = (int *)piVar3[1];
      if (piVar4[4] != 0) break;
      piVar5 = *(int **)piVar4[1];
      if (piVar4 == piVar5) {
        iVar1 = ((undefined4 *)piVar4[1])[2];
        if (*(int *)(iVar1 + 0x10) == 0) {
          piVar4[4] = 1;
          *(undefined4 *)(iVar1 + 0x10) = 1;
          *(undefined4 *)(*(int *)(piVar3[1] + 4) + 0x10) = 0;
          piVar3 = *(int **)(piVar3[1] + 4);
        }
        else {
          if (piVar3 == (int *)piVar4[2]) {
            piVar3 = (int *)piVar4[2];
            piVar4[2] = *piVar3;
            if (*piVar3 != DAT_009d0c44) {
              *(int **)(*piVar3 + 4) = piVar4;
            }
            piVar3[1] = piVar4[1];
            if (piVar4 == *(int **)(*(int *)(in_ECX + 4) + 4)) {
              *(int **)(*(int *)(in_ECX + 4) + 4) = piVar3;
            }
            else {
              piVar5 = (int *)piVar4[1];
              if (piVar4 == (int *)*piVar5) {
                *piVar5 = (int)piVar3;
              }
              else {
                piVar5[2] = (int)piVar3;
              }
            }
            *piVar3 = (int)piVar4;
            piVar4[1] = (int)piVar3;
            piVar3 = piVar4;
          }
          *(undefined4 *)(piVar3[1] + 0x10) = 1;
          *(undefined4 *)(*(int *)(piVar3[1] + 4) + 0x10) = 0;
          piVar4 = *(int **)(piVar3[1] + 4);
          piVar5 = (int *)*piVar4;
          *piVar4 = piVar5[2];
          if (piVar5[2] != DAT_009d0c44) {
            *(int **)(piVar5[2] + 4) = piVar4;
          }
          piVar5[1] = piVar4[1];
          if (piVar4 == *(int **)(*(int *)(in_ECX + 4) + 4)) {
            *(int **)(*(int *)(in_ECX + 4) + 4) = piVar5;
            piVar5[2] = (int)piVar4;
          }
          else {
            piVar2 = (int *)piVar4[1];
            if (piVar4 == (int *)piVar2[2]) {
              piVar2[2] = (int)piVar5;
              piVar5[2] = (int)piVar4;
            }
            else {
              *piVar2 = (int)piVar5;
              piVar5[2] = (int)piVar4;
            }
          }
LAB_00573fbc:
          piVar4[1] = (int)piVar5;
        }
      }
      else {
        if (piVar5[4] != 0) {
          if (piVar3 == (int *)*piVar4) {
            iVar1 = *piVar4;
            *piVar4 = *(int *)(iVar1 + 8);
            if (*(int *)(iVar1 + 8) != DAT_009d0c44) {
              *(int **)(*(int *)(iVar1 + 8) + 4) = piVar4;
            }
            *(int *)(iVar1 + 4) = piVar4[1];
            if (piVar4 == *(int **)(*(int *)(in_ECX + 4) + 4)) {
              *(int *)(*(int *)(in_ECX + 4) + 4) = iVar1;
            }
            else {
              piVar3 = (int *)piVar4[1];
              if (piVar4 == (int *)piVar3[2]) {
                piVar3[2] = iVar1;
              }
              else {
                *piVar3 = iVar1;
              }
            }
            *(int **)(iVar1 + 8) = piVar4;
            piVar4[1] = iVar1;
            piVar3 = piVar4;
          }
          *(undefined4 *)(piVar3[1] + 0x10) = 1;
          *(undefined4 *)(*(int *)(piVar3[1] + 4) + 0x10) = 0;
          piVar4 = *(int **)(piVar3[1] + 4);
          piVar5 = (int *)piVar4[2];
          piVar4[2] = *piVar5;
          if (*piVar5 != DAT_009d0c44) {
            *(int **)(*piVar5 + 4) = piVar4;
          }
          piVar5[1] = piVar4[1];
          if (piVar4 == *(int **)(*(int *)(in_ECX + 4) + 4)) {
            *(int **)(*(int *)(in_ECX + 4) + 4) = piVar5;
          }
          else {
            piVar2 = (int *)piVar4[1];
            if (piVar4 == (int *)*piVar2) {
              *piVar2 = (int)piVar5;
            }
            else {
              piVar2[2] = (int)piVar5;
            }
          }
          *piVar5 = (int)piVar4;
          goto LAB_00573fbc;
        }
        piVar4[4] = 1;
        piVar5[4] = 1;
        *(undefined4 *)(*(int *)(piVar3[1] + 4) + 0x10) = 0;
        piVar3 = *(int **)(piVar3[1] + 4);
      }
    } while (piVar3 != *(int **)(*(int *)(in_ECX + 4) + 4));
  }
  *(undefined4 *)(*(int *)(*(int *)(in_ECX + 4) + 4) + 0x10) = 1;
  *in_stack_00000004 = extraout_EAX;
  return (int)in_stack_00000004;
}
