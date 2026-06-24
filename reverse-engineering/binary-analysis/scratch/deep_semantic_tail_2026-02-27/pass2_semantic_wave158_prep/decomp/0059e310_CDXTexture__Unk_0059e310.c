/* address: 0x0059e310 */
/* name: CDXTexture__Unk_0059e310 */
/* signature: void __thiscall CDXTexture__Unk_0059e310(void * this, void * param_1, int param_2) */


void __thiscall CDXTexture__Unk_0059e310(void *this,void *param_1,int param_2)

{
  int *piVar1;
  undefined4 *puVar2;
  int *piVar3;
  undefined1 *puVar4;
  int in_EAX;
  byte *pbVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;

  if (in_EAX == 0) {
    iVar9 = *(int *)((int)this + (int)param_1 * 4 + 0x58);
  }
  else {
    iVar9 = *(int *)((int)this + (int)param_1 * 4 + 0x68);
    param_1 = (void *)((int)param_1 + 0x10);
  }
  if (iVar9 == 0) {
    puVar2 = *(undefined4 **)this;
    puVar2[5] = 0x32;
    puVar2[6] = param_1;
    (*(code *)*puVar2)(this);
  }
  if (*(int *)(iVar9 + 0x114) == 0) {
    CDXTexture__Helper_0059e0b0(0xc4);
    iVar8 = 0;
    pbVar5 = (byte *)(iVar9 + 7);
    iVar7 = 2;
    do {
      iVar8 = (uint)*pbVar5 + iVar8 +
              (uint)pbVar5[-6] + (uint)pbVar5[-5] + (uint)pbVar5[-4] + (uint)pbVar5[-3] +
              (uint)pbVar5[-2] + (uint)pbVar5[-1] + (uint)pbVar5[1];
      pbVar5 = pbVar5 + 8;
      iVar7 = iVar7 + -1;
    } while (iVar7 != 0);
    piVar3 = *(int **)((int)this + 0x18);
    puVar4 = (undefined1 *)*piVar3;
    *puVar4 = (char)((uint)(iVar8 + 0x13) >> 8);
    *piVar3 = (int)(puVar4 + 1);
    piVar1 = piVar3 + 1;
    *piVar1 = *piVar1 + -1;
    if ((*piVar1 == 0) && (iVar7 = (*(code *)piVar3[3])(this), iVar7 == 0)) {
      puVar2 = *(undefined4 **)this;
      puVar2[5] = 0x18;
      (*(code *)*puVar2)(this);
    }
    piVar3 = *(int **)((int)this + 0x18);
    puVar4 = (undefined1 *)*piVar3;
    *puVar4 = (char)(iVar8 + 0x13);
    *piVar3 = (int)(puVar4 + 1);
    piVar1 = piVar3 + 1;
    *piVar1 = *piVar1 + -1;
    if ((*piVar1 == 0) && (iVar7 = (*(code *)piVar3[3])(this), iVar7 == 0)) {
      puVar2 = *(undefined4 **)this;
      puVar2[5] = 0x18;
      (*(code *)*puVar2)(this);
    }
    piVar3 = *(int **)((int)this + 0x18);
    puVar4 = (undefined1 *)*piVar3;
    *puVar4 = param_1._0_1_;
    *piVar3 = (int)(puVar4 + 1);
    piVar1 = piVar3 + 1;
    *piVar1 = *piVar1 + -1;
    if ((*piVar1 == 0) && (iVar7 = (*(code *)piVar3[3])(this), iVar7 == 0)) {
      puVar2 = *(undefined4 **)this;
      puVar2[5] = 0x18;
      (*(code *)*puVar2)(this);
    }
    iVar7 = 1;
    do {
      puVar2 = *(undefined4 **)((int)this + 0x18);
      puVar4 = (undefined1 *)*puVar2;
      *puVar4 = *(undefined1 *)(iVar7 + iVar9);
      *puVar2 = puVar4 + 1;
      piVar1 = puVar2 + 1;
      *piVar1 = *piVar1 + -1;
      if ((*piVar1 == 0) && (iVar6 = (*(code *)puVar2[3])(this), iVar6 == 0)) {
        puVar2 = *(undefined4 **)this;
        puVar2[5] = 0x18;
        (*(code *)*puVar2)(this);
      }
      iVar7 = iVar7 + 1;
    } while (iVar7 < 0x11);
    iVar7 = 0;
    if (0 < iVar8) {
      do {
        puVar2 = *(undefined4 **)((int)this + 0x18);
        puVar4 = (undefined1 *)*puVar2;
        *puVar4 = *(undefined1 *)(iVar7 + 0x11 + iVar9);
        *puVar2 = puVar4 + 1;
        piVar1 = puVar2 + 1;
        *piVar1 = *piVar1 + -1;
        if ((*piVar1 == 0) && (iVar6 = (*(code *)puVar2[3])(this), iVar6 == 0)) {
          puVar2 = *(undefined4 **)this;
          puVar2[5] = 0x18;
          (*(code *)*puVar2)(this);
        }
        iVar7 = iVar7 + 1;
      } while (iVar7 < iVar8);
    }
    *(undefined4 *)(iVar9 + 0x114) = 1;
  }
  return;
}
