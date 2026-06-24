/* address: 0x00599e48 */
/* name: CFastVB__ResolveCommonLeafFormat */
/* signature: int __stdcall CFastVB__ResolveCommonLeafFormat(int param_1, int param_2, void * param_3) */


int CFastVB__ResolveCommonLeafFormat(int param_1,int param_2,void *param_3)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  bool bVar7;
  bool bVar8;

  if ((((param_1 == 0) || (*(int *)(param_1 + 4) != 8)) || (param_2 == 0)) ||
     (*(int *)(param_2 + 4) != 8)) {
LAB_00599fe9:
    iVar4 = -0x7fffbffb;
  }
  else {
    iVar4 = *(int *)(param_1 + 0x14);
    iVar1 = *(int *)(param_2 + 0x14);
    if (iVar4 == iVar1) {
      *(int *)param_3 = iVar4;
    }
    else {
      uVar6 = *(uint *)(&DAT_005f2908 + iVar1 * 8);
      if (*(uint *)(&DAT_005f2908 + iVar1 * 8) < *(uint *)(&DAT_005f2908 + iVar4 * 8)) {
        uVar6 = *(uint *)(&DAT_005f2908 + iVar4 * 8);
      }
      uVar2 = *(uint *)(&DAT_005f290c + iVar4 * 8) & *(uint *)(&DAT_005f290c + iVar1 * 8);
      if ((uVar2 & 1) == 0) {
        if ((uVar2 & 4) == 0) {
          if ((uVar2 & 2) == 0) {
            if ((uVar2 & 8) == 0) {
              if ((uVar2 & 0x10) != 0) {
                uVar6 = 0;
                do {
                  iVar3 = iVar1;
                  iVar5 = iVar4;
                  if (uVar6 == 0) {
                    iVar3 = iVar4;
                    iVar5 = iVar1;
                  }
                  if (iVar5 == 0xd) {
LAB_00599ff4:
                    *(int *)param_3 = iVar3;
                    goto LAB_00599ff9;
                  }
                  if (iVar5 == 0xf) {
                    if (0xe < iVar3) {
                      bVar8 = SBORROW4(iVar3,0x13);
                      iVar5 = -0x13;
                      bVar7 = iVar3 == 0x13;
LAB_00599fe1:
                      if (bVar7 || bVar8 != iVar3 + iVar5 < 0) goto LAB_00599ff4;
                    }
                  }
                  else if ((iVar5 == 0x14) && (0x13 < iVar3)) {
                    bVar8 = SBORROW4(iVar3,0x18);
                    iVar5 = -0x18;
                    bVar7 = iVar3 == 0x18;
                    goto LAB_00599fe1;
                  }
                  uVar6 = uVar6 + 1;
                } while (uVar6 < 2);
              }
              goto LAB_00599fe9;
            }
            if (uVar6 == 0) {
              *(undefined4 *)param_3 = 9;
            }
            else if ((uVar6 == 8) || (uVar6 == 0x10)) {
              *(undefined4 *)param_3 = 10;
            }
            else if (uVar6 == 0x20) {
              *(undefined4 *)param_3 = 0xb;
            }
            else if (uVar6 == 0x40) {
              *(undefined4 *)param_3 = 0xc;
            }
          }
          else if (uVar6 == 0) {
            *(undefined4 *)param_3 = 1;
          }
          else if (uVar6 == 8) {
            *(undefined4 *)param_3 = 2;
          }
          else if (uVar6 == 0x10) {
            *(undefined4 *)param_3 = 3;
          }
          else if ((uVar6 == 0x20) || (uVar6 == 0x40)) {
            *(undefined4 *)param_3 = 4;
          }
        }
        else if (uVar6 == 0) {
          *(undefined4 *)param_3 = 5;
        }
        else if (uVar6 == 8) {
          *(undefined4 *)param_3 = 6;
        }
        else if (uVar6 == 0x10) {
          *(undefined4 *)param_3 = 7;
        }
        else if ((uVar6 == 0x20) || (uVar6 == 0x40)) {
          *(undefined4 *)param_3 = 8;
        }
      }
      else {
        *(undefined4 *)param_3 = 0;
      }
    }
LAB_00599ff9:
    iVar4 = 0;
  }
  return iVar4;
}
