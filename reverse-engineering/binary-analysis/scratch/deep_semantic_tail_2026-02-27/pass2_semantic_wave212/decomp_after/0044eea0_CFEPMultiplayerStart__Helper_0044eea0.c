/* address: 0x0044eea0 */
/* name: CFEPMultiplayerStart__Helper_0044eea0 */
/* signature: int __cdecl CFEPMultiplayerStart__Helper_0044eea0(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __cdecl CFEPMultiplayerStart__Helper_0044eea0(int param_1)

{
  byte bVar1;
  int *piVar2;
  byte *pbVar3;
  int iVar4;
  undefined4 *puVar5;
  int iVar6;
  byte *pbVar7;
  bool bVar8;

  DAT_0089da3c = DAT_0089da34;
  if (DAT_0089da34 == (undefined4 *)0x0) {
    piVar2 = (int *)0x0;
  }
  else {
    piVar2 = (int *)*DAT_0089da34;
  }
  if (piVar2 != (int *)0x0) {
    while (DAT_0089d94c != *piVar2) {
      DAT_0089da3c = (undefined4 *)DAT_0089da3c[1];
      if (DAT_0089da3c == (undefined4 *)0x0) {
        piVar2 = (int *)0x0;
      }
      else {
        piVar2 = (int *)*DAT_0089da3c;
      }
      if (piVar2 == (int *)0x0) {
        return 0;
      }
    }
    if ((piVar2 != (int *)0x0) && (piVar2 = CSPtrSet__First(&DAT_0089da34), piVar2 != (int *)0x0)) {
      while (DAT_0089d94c != *piVar2) {
        DAT_0089da3c = (undefined4 *)DAT_0089da3c[1];
        if (DAT_0089da3c == (undefined4 *)0x0) {
          piVar2 = (int *)0x0;
        }
        else {
          piVar2 = (int *)*DAT_0089da3c;
        }
        if (piVar2 == (int *)0x0) {
          return 0;
        }
      }
      if (piVar2 != (int *)0x0) {
        puVar5 = (undefined4 *)piVar2[5];
        iVar6 = 0;
        piVar2[7] = (int)puVar5;
        if (puVar5 == (undefined4 *)0x0) {
          puVar5 = (undefined4 *)0x0;
        }
        else {
          puVar5 = (undefined4 *)*puVar5;
        }
        if (puVar5 != (undefined4 *)0x0) {
          while (iVar6 != param_1) {
            iVar6 = iVar6 + 1;
            puVar5 = *(undefined4 **)(piVar2[7] + 4);
            piVar2[7] = (int)puVar5;
            if (puVar5 == (undefined4 *)0x0) {
              puVar5 = (undefined4 *)0x0;
            }
            else {
              puVar5 = (undefined4 *)*puVar5;
            }
            if (puVar5 == (undefined4 *)0x0) {
              return 0;
            }
          }
          if ((byte *)*puVar5 != (byte *)0x0) {
            _DAT_006602a8 = DAT_006602a0;
            if (DAT_006602a0 == (int *)0x0) {
              iVar6 = 0;
            }
            else {
              iVar6 = *DAT_006602a0;
            }
            while (iVar6 != 0) {
              pbVar3 = *(byte **)(iVar6 + 0xa8);
              pbVar7 = (byte *)*puVar5;
              do {
                bVar1 = *pbVar3;
                bVar8 = bVar1 < *pbVar7;
                if (bVar1 != *pbVar7) {
LAB_0044efd5:
                  iVar4 = (1 - (uint)bVar8) - (uint)(bVar8 != 0);
                  goto LAB_0044efda;
                }
                if (bVar1 == 0) break;
                bVar1 = pbVar3[1];
                bVar8 = bVar1 < pbVar7[1];
                if (bVar1 != pbVar7[1]) goto LAB_0044efd5;
                pbVar3 = pbVar3 + 2;
                pbVar7 = pbVar7 + 2;
              } while (bVar1 != 0);
              iVar4 = 0;
LAB_0044efda:
              if (iVar4 == 0) {
                if (iVar6 == 0) {
                  return 0;
                }
                _DAT_006602a8 = _DAT_006602a8;
                return (uint)(*(int *)(iVar6 + 0x60) != 0) + *(int *)(iVar6 + 0x4c);
              }
              _DAT_006602a8 = (int *)_DAT_006602a8[1];
              if (_DAT_006602a8 == (int *)0x0) {
                iVar6 = 0;
              }
              else {
                iVar6 = *_DAT_006602a8;
              }
            }
          }
        }
      }
    }
  }
  return 0;
}
