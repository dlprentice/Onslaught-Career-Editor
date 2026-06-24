/* address: 0x004127a0 */
/* name: CGeneralVolume__Unk_004127a0 */
/* signature: void __thiscall CGeneralVolume__Unk_004127a0(void * this, void * param_1, void * param_2) */


void __thiscall CGeneralVolume__Unk_004127a0(void *this,void *param_1,void *param_2)

{
  byte bVar1;
  int *piVar2;
  byte *pbVar3;
  int iVar4;
  int iVar5;
  byte *pbVar6;
  bool bVar7;

  piVar2 = *(int **)this;
  *(int **)((int)this + 8) = piVar2;
  if (piVar2 == (int *)0x0) {
    iVar5 = 0;
  }
  else {
    iVar5 = *piVar2;
  }
  do {
    if (iVar5 == 0) {
      return;
    }
    pbVar6 = (byte *)**(undefined4 **)(iVar5 + 0xa4);
    pbVar3 = param_1;
    do {
      bVar1 = *pbVar3;
      bVar7 = bVar1 < *pbVar6;
      if (bVar1 != *pbVar6) {
LAB_004127ee:
        iVar4 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
        goto LAB_004127f3;
      }
      if (bVar1 == 0) break;
      bVar1 = pbVar3[1];
      bVar7 = bVar1 < pbVar6[1];
      if (bVar1 != pbVar6[1]) goto LAB_004127ee;
      pbVar3 = pbVar3 + 2;
      pbVar6 = pbVar6 + 2;
    } while (bVar1 != 0);
    iVar4 = 0;
LAB_004127f3:
    if (iVar4 == 0) {
      *(undefined4 *)(iVar5 + 0x9c) = 1;
    }
    piVar2 = *(int **)(*(int *)((int)this + 8) + 4);
    *(int **)((int)this + 8) = piVar2;
    if (piVar2 == (int *)0x0) {
      iVar5 = 0;
    }
    else {
      iVar5 = *piVar2;
    }
  } while( true );
}
