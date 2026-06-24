/* address: 0x00414a40 */
/* name: CGeneralVolume__Unk_00414a40 */
/* signature: void __thiscall CGeneralVolume__Unk_00414a40(void * this, void * param_1, void * param_2) */


void __thiscall CGeneralVolume__Unk_00414a40(void *this,void *param_1,void *param_2)

{
  byte bVar1;
  int *piVar2;
  byte *pbVar3;
  int iVar4;
  int iVar5;
  byte *pbVar6;
  bool bVar7;

  piVar2 = *(int **)this;
  if (piVar2 == (int *)0x0) {
    iVar5 = 0;
  }
  else {
    iVar5 = *piVar2;
  }
  while (iVar5 != 0) {
    pbVar6 = (byte *)**(undefined4 **)(iVar5 + 0xa4);
    pbVar3 = param_1;
    do {
      bVar1 = *pbVar3;
      bVar7 = bVar1 < *pbVar6;
      if (bVar1 != *pbVar6) {
LAB_00414a8b:
        iVar4 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
        goto LAB_00414a90;
      }
      if (bVar1 == 0) break;
      bVar1 = pbVar3[1];
      bVar7 = bVar1 < pbVar6[1];
      if (bVar1 != pbVar6[1]) goto LAB_00414a8b;
      pbVar3 = pbVar3 + 2;
      pbVar6 = pbVar6 + 2;
    } while (bVar1 != 0);
    iVar4 = 0;
LAB_00414a90:
    if (iVar4 == 0) {
      *(undefined4 *)(iVar5 + 0x9c) = 0;
      iVar4 = CGeneralVolume__Unk_00414030(this);
      if (iVar4 == iVar5) {
        CGeneralVolume__Unk_00413eb0(this);
      }
    }
    piVar2 = (int *)piVar2[1];
    if (piVar2 == (int *)0x0) {
      iVar5 = 0;
    }
    else {
      iVar5 = *piVar2;
    }
  }
  pbVar6 = (byte *)**(undefined4 **)(*(int *)((int)this + 0x18) + 0xa4);
  do {
    bVar1 = *(byte *)param_1;
    bVar7 = bVar1 < *pbVar6;
    if (bVar1 != *pbVar6) {
LAB_00414afb:
      iVar5 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
      goto LAB_00414b00;
    }
    if (bVar1 == 0) break;
    bVar1 = *(byte *)((int)param_1 + 1);
    bVar7 = bVar1 < pbVar6[1];
    if (bVar1 != pbVar6[1]) goto LAB_00414afb;
    param_1 = (void *)((int)param_1 + 2);
    pbVar6 = pbVar6 + 2;
  } while (bVar1 != 0);
  iVar5 = 0;
LAB_00414b00:
  if (iVar5 == 0) {
    *(undefined4 *)(*(int *)((int)this + 0x18) + 0x9c) = 0;
  }
  iVar5 = CGeneralVolume__Unk_00414030(this);
  if (iVar5 == *(int *)((int)this + 0x18)) {
    CGeneralVolume__Unk_00413eb0(this);
  }
  return;
}
