/* address: 0x0059e580 */
/* name: CDXTexture__WriteJpegFrameHeader */
/* signature: void __fastcall CDXTexture__WriteJpegFrameHeader(void * param_1) */


void __fastcall CDXTexture__WriteJpegFrameHeader(void *param_1)

{
  int *piVar1;
  int *piVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  undefined1 *puVar5;
  char *pcVar6;
  int in_EAX;
  int iVar7;
  int iVar8;
  undefined1 *puVar9;

  CDXTexture__Helper_0059e0b0(in_EAX);
  iVar8 = *(int *)((int)param_1 + 0x3c) * 3 + 8;
  piVar2 = *(int **)((int)param_1 + 0x18);
  puVar9 = (undefined1 *)*piVar2;
  *puVar9 = (char)((uint)iVar8 >> 8);
  *piVar2 = (int)(puVar9 + 1);
  piVar1 = piVar2 + 1;
  *piVar1 = *piVar1 + -1;
  if ((*piVar1 == 0) && (iVar7 = (*(code *)piVar2[3])(param_1), iVar7 == 0)) {
    puVar3 = *(undefined4 **)param_1;
    puVar3[5] = 0x18;
    (*(code *)*puVar3)(param_1);
  }
  piVar2 = *(int **)((int)param_1 + 0x18);
  puVar9 = (undefined1 *)*piVar2;
  *puVar9 = (char)iVar8;
  *piVar2 = (int)(puVar9 + 1);
  piVar1 = piVar2 + 1;
  *piVar1 = *piVar1 + -1;
  if ((*piVar1 == 0) && (iVar8 = (*(code *)piVar2[3])(param_1), iVar8 == 0)) {
    puVar3 = *(undefined4 **)param_1;
    puVar3[5] = 0x18;
    (*(code *)*puVar3)(param_1);
  }
  if ((0xffff < *(int *)((int)param_1 + 0x20)) || (0xffff < *(int *)((int)param_1 + 0x1c))) {
    puVar3 = *(undefined4 **)param_1;
    puVar3[5] = 0x29;
    puVar3[6] = 0xffff;
    (*(code *)*puVar3)(param_1);
  }
  puVar3 = *(undefined4 **)((int)param_1 + 0x18);
  puVar9 = (undefined1 *)*puVar3;
  *puVar9 = *(undefined1 *)((int)param_1 + 0x38);
  *puVar3 = puVar9 + 1;
  piVar1 = puVar3 + 1;
  *piVar1 = *piVar1 + -1;
  if ((*piVar1 == 0) && (iVar8 = (*(code *)puVar3[3])(param_1), iVar8 == 0)) {
    puVar3 = *(undefined4 **)param_1;
    puVar3[5] = 0x18;
    (*(code *)*puVar3)(param_1);
  }
  piVar2 = *(int **)((int)param_1 + 0x18);
  uVar4 = *(undefined4 *)((int)param_1 + 0x20);
  puVar9 = (undefined1 *)*piVar2;
  *puVar9 = (char)((uint)uVar4 >> 8);
  *piVar2 = (int)(puVar9 + 1);
  piVar1 = piVar2 + 1;
  *piVar1 = *piVar1 + -1;
  if ((*piVar1 == 0) && (iVar8 = (*(code *)piVar2[3])(param_1), iVar8 == 0)) {
    puVar3 = *(undefined4 **)param_1;
    puVar3[5] = 0x18;
    (*(code *)*puVar3)(param_1);
  }
  piVar2 = *(int **)((int)param_1 + 0x18);
  puVar9 = (undefined1 *)*piVar2;
  *puVar9 = (char)uVar4;
  *piVar2 = (int)(puVar9 + 1);
  piVar1 = piVar2 + 1;
  *piVar1 = *piVar1 + -1;
  if ((*piVar1 == 0) && (iVar8 = (*(code *)piVar2[3])(param_1), iVar8 == 0)) {
    puVar3 = *(undefined4 **)param_1;
    puVar3[5] = 0x18;
    (*(code *)*puVar3)(param_1);
  }
  piVar2 = *(int **)((int)param_1 + 0x18);
  uVar4 = *(undefined4 *)((int)param_1 + 0x1c);
  puVar9 = (undefined1 *)*piVar2;
  *puVar9 = (char)((uint)uVar4 >> 8);
  *piVar2 = (int)(puVar9 + 1);
  piVar1 = piVar2 + 1;
  *piVar1 = *piVar1 + -1;
  if ((*piVar1 == 0) && (iVar8 = (*(code *)piVar2[3])(param_1), iVar8 == 0)) {
    puVar3 = *(undefined4 **)param_1;
    puVar3[5] = 0x18;
    (*(code *)*puVar3)(param_1);
  }
  piVar2 = *(int **)((int)param_1 + 0x18);
  puVar9 = (undefined1 *)*piVar2;
  *puVar9 = (char)uVar4;
  *piVar2 = (int)(puVar9 + 1);
  piVar1 = piVar2 + 1;
  *piVar1 = *piVar1 + -1;
  if ((*piVar1 == 0) && (iVar8 = (*(code *)piVar2[3])(param_1), iVar8 == 0)) {
    puVar3 = *(undefined4 **)param_1;
    puVar3[5] = 0x18;
    (*(code *)*puVar3)(param_1);
  }
  puVar3 = *(undefined4 **)((int)param_1 + 0x18);
  puVar9 = (undefined1 *)*puVar3;
  *puVar9 = *(undefined1 *)((int)param_1 + 0x3c);
  *puVar3 = puVar9 + 1;
  piVar1 = puVar3 + 1;
  *piVar1 = *piVar1 + -1;
  if ((*piVar1 == 0) && (iVar8 = (*(code *)puVar3[3])(param_1), iVar8 == 0)) {
    puVar3 = *(undefined4 **)param_1;
    puVar3[5] = 0x18;
    (*(code *)*puVar3)(param_1);
  }
  puVar9 = *(undefined1 **)((int)param_1 + 0x44);
  iVar8 = 0;
  if (0 < *(int *)((int)param_1 + 0x3c)) {
    do {
      puVar3 = *(undefined4 **)((int)param_1 + 0x18);
      puVar5 = (undefined1 *)*puVar3;
      *puVar5 = *puVar9;
      *puVar3 = puVar5 + 1;
      piVar1 = puVar3 + 1;
      *piVar1 = *piVar1 + -1;
      if ((*piVar1 == 0) && (iVar7 = (*(code *)puVar3[3])(param_1), iVar7 == 0)) {
        puVar3 = *(undefined4 **)param_1;
        puVar3[5] = 0x18;
        (*(code *)*puVar3)(param_1);
      }
      piVar2 = *(int **)((int)param_1 + 0x18);
      pcVar6 = (char *)*piVar2;
      *pcVar6 = puVar9[8] * '\x10' + puVar9[0xc];
      *piVar2 = (int)(pcVar6 + 1);
      piVar1 = piVar2 + 1;
      *piVar1 = *piVar1 + -1;
      if ((*piVar1 == 0) && (iVar7 = (*(code *)piVar2[3])(param_1), iVar7 == 0)) {
        puVar3 = *(undefined4 **)param_1;
        puVar3[5] = 0x18;
        (*(code *)*puVar3)(param_1);
      }
      puVar3 = *(undefined4 **)((int)param_1 + 0x18);
      puVar5 = (undefined1 *)*puVar3;
      *puVar5 = puVar9[0x10];
      *puVar3 = puVar5 + 1;
      piVar1 = puVar3 + 1;
      *piVar1 = *piVar1 + -1;
      if ((*piVar1 == 0) && (iVar7 = (*(code *)puVar3[3])(param_1), iVar7 == 0)) {
        puVar3 = *(undefined4 **)param_1;
        puVar3[5] = 0x18;
        (*(code *)*puVar3)(param_1);
      }
      iVar8 = iVar8 + 1;
      puVar9 = puVar9 + 0x54;
    } while (iVar8 < *(int *)((int)param_1 + 0x3c));
  }
  return;
}
