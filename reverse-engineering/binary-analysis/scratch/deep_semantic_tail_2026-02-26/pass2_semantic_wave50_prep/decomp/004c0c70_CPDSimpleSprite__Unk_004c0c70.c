/* address: 0x004c0c70 */
/* name: CPDSimpleSprite__Unk_004c0c70 */
/* signature: int CPDSimpleSprite__Unk_004c0c70(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CPDSimpleSprite__Unk_004c0c70(void)

{
  float fVar1;
  float fVar2;
  uint uVar3;
  int extraout_EAX;
  int extraout_EAX_00;
  int unaff_EDI;
  float10 extraout_ST0;
  float10 fVar4;
  float10 extraout_ST0_00;
  float10 fVar5;
  float10 extraout_ST0_01;
  float10 extraout_ST0_02;
  float in_stack_00000004;
  float *in_stack_00000008;
  float *in_stack_0000000c;
  float *in_stack_00000010;
  float *in_stack_00000014;
  undefined4 in_stack_00000018;
  int in_stack_0000001c;
  float in_stack_00000020;

  fVar2 = in_stack_00000020;
  fVar1 = in_stack_0000000c[1];
  if (fVar1 == 0.0) {
    in_stack_00000020 = *in_stack_0000000c;
  }
  else {
    if (*(int *)((int)fVar1 + 0x84) != 0) {
      CPDSimpleSprite__Helper_004c10c0
                ((void *)((int)fVar1 + 0x88),DAT_009c6400,in_stack_00000020,unaff_EDI);
      CPDSimpleSprite__Helper_0055e3ea();
    }
    CPDSimpleSprite__Unk_004c0c70();
    in_stack_00000020 = (float)(extraout_ST0 * (float10)*in_stack_0000000c);
  }
  fVar1 = in_stack_00000010[1];
  if (fVar1 == 0.0) {
    fVar4 = (float10)*in_stack_00000010;
  }
  else {
    if (*(int *)((int)fVar1 + 0x84) != 0) {
      CPDSimpleSprite__Helper_004c10c0((void *)((int)fVar1 + 0x88),DAT_009c6400,fVar2,unaff_EDI);
      CPDSimpleSprite__Helper_0055e3ea();
    }
    CPDSimpleSprite__Unk_004c0c70();
    fVar4 = extraout_ST0_00 * (float10)*in_stack_00000010;
  }
  in_stack_00000004 = (float)((float10)in_stack_00000020 * (float10)in_stack_00000004 + fVar4);
  switch(in_stack_00000018) {
  case 1:
    fVar4 = (float10)in_stack_00000004 * (float10)in_stack_00000004;
    break;
  case 2:
    fVar4 = ROUND((float10)1.4426950408889634 * (float10)in_stack_00000004);
    fVar5 = (float10)f2xm1((float10)1.4426950408889634 * (float10)in_stack_00000004 - fVar4);
    fVar4 = (float10)fscale((float10)1 + fVar5,fVar4);
    break;
  case 3:
    fVar4 = (float10)fsin((float10)in_stack_00000004);
    break;
  case 4:
    fVar4 = (float10)fcos((float10)in_stack_00000004);
    break;
  case 5:
    if (in_stack_00000004 == _DAT_005d856c) goto switchD_004c0e09_caseD_7;
    fVar4 = (float10)_DAT_005d8568 / (float10)in_stack_00000004;
    break;
  case 6:
    fVar4 = (float10)0.6931471805599453 * (float10)in_stack_00000004;
    break;
  default:
    goto switchD_004c0e09_caseD_7;
  case 10:
    uVar3 = _rand();
    fVar4 = (float10)(int)((uVar3 & 0xff) - 0x80) * (float10)_DAT_005ddac8;
  }
  in_stack_00000004 = (float)fVar4;
switchD_004c0e09_caseD_7:
  fVar1 = in_stack_00000008[1];
  if (fVar1 == 0.0) {
    in_stack_00000020 = *in_stack_00000008;
  }
  else {
    if (*(int *)((int)fVar1 + 0x84) != 0) {
      CPDSimpleSprite__Helper_004c10c0((void *)((int)fVar1 + 0x88),DAT_009c6400,fVar2,unaff_EDI);
      CPDSimpleSprite__Helper_0055e3ea();
    }
    CPDSimpleSprite__Unk_004c0c70();
    in_stack_00000020 = (float)(extraout_ST0_01 * (float10)*in_stack_00000008);
  }
  fVar1 = in_stack_00000014[1];
  if (fVar1 == 0.0) {
    fVar4 = (float10)*in_stack_00000014;
  }
  else {
    if (*(int *)((int)fVar1 + 0x84) != 0) {
      CPDSimpleSprite__Helper_004c10c0((void *)((int)fVar1 + 0x88),DAT_009c6400,fVar2,unaff_EDI);
      CPDSimpleSprite__Helper_0055e3ea();
    }
    CPDSimpleSprite__Unk_004c0c70();
    fVar4 = extraout_ST0_02 * (float10)*in_stack_00000014;
  }
  fVar4 = (float10)in_stack_00000020 * (float10)in_stack_00000004 + fVar4;
  if (in_stack_0000001c == 0) {
    fVar5 = (float10)_DAT_005d8568;
    if (fVar4 >= fVar5 && (fVar4 == fVar5) == 0) {
      return (uint)(ushort)((ushort)(fVar4 < fVar5) << 8 | (ushort)(NAN(fVar4) || NAN(fVar5)) << 10
                           | (ushort)(fVar4 == fVar5) << 0xe);
    }
    fVar5 = (float10)_DAT_005d8be0;
    uVar3 = (uint)(ushort)((ushort)(fVar4 < fVar5) << 8 | (ushort)(NAN(fVar4) || NAN(fVar5)) << 10 |
                          (ushort)(fVar4 == fVar5) << 0xe);
  }
  else {
    uVar3 = in_stack_0000001c - 1;
    if (uVar3 == 0) {
      if ((float10)_DAT_005d8be0 < fVar4) {
        CPDSimpleSprite__Helper_0055e3ea();
        return extraout_EAX;
      }
      CPDSimpleSprite__Helper_0055e3ea();
      return extraout_EAX_00;
    }
  }
  return uVar3;
}
