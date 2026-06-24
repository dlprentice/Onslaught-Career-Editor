/* address: 0x00511c10 */
/* name: CVBufTexture__SetNameListIndexOrMinusOne */
/* signature: void __thiscall CVBufTexture__SetNameListIndexOrMinusOne(void * this, int param_1, void * param_2) */


void __thiscall CVBufTexture__SetNameListIndexOrMinusOne(void *this,int param_1,void *param_2)

{
  byte bVar1;
  int *piVar2;
  byte *pbVar3;
  int iVar4;
  byte *pbVar5;
  int iVar6;
  bool bVar7;

  if (param_1 != 0) {
    iVar6 = 0;
    piVar2 = (int *)*DAT_008553f8;
    DAT_008553f8[2] = (int)piVar2;
    if (piVar2 == (int *)0x0) {
      iVar4 = 0;
    }
    else {
      iVar4 = *piVar2;
    }
    while (iVar4 != 0) {
      pbVar5 = *(byte **)(iVar4 + 0x30);
      pbVar3 = (byte *)param_1;
      do {
        bVar1 = *pbVar3;
        bVar7 = bVar1 < *pbVar5;
        if (bVar1 != *pbVar5) {
LAB_00511c60:
          iVar4 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
          goto LAB_00511c65;
        }
        if (bVar1 == 0) break;
        bVar1 = pbVar3[1];
        bVar7 = bVar1 < pbVar5[1];
        if (bVar1 != pbVar5[1]) goto LAB_00511c60;
        pbVar3 = pbVar3 + 2;
        pbVar5 = pbVar5 + 2;
      } while (bVar1 != 0);
      iVar4 = 0;
LAB_00511c65:
      if (iVar4 == 0) {
        *(int *)((int)this + 8) = iVar6;
        return;
      }
      iVar6 = iVar6 + 1;
      piVar2 = *(int **)(DAT_008553f8[2] + 4);
      DAT_008553f8[2] = (int)piVar2;
      if (piVar2 == (int *)0x0) {
        iVar4 = 0;
      }
      else {
        iVar4 = *piVar2;
      }
    }
  }
  *(undefined4 *)((int)this + 8) = 0xffffffff;
  return;
}
