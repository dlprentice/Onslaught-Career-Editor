/* address: 0x00542f90 */
/* name: CDXImposter__BuildQuadGeometry */
/* signature: int CDXImposter__BuildQuadGeometry(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXImposter__BuildQuadGeometry(void)

{
  float fVar1;
  undefined4 in_EAX;
  short *psVar2;
  short sVar3;
  void *unaff_EBX;
  float *in_stack_00000008;
  float *in_stack_0000000c;
  float in_stack_00000010;
  float in_stack_00000018;
  float in_stack_0000001c;
  float in_stack_00000020;
  float in_stack_00000024;
  int in_stack_00000028;
  float local_30;
  float local_2c;
  float local_28;
  float local_20;
  float local_1c;
  float local_18;
  float local_10;
  float local_c;
  float local_8;

  local_30 = in_stack_0000000c[2] * in_stack_00000008[1] -
             in_stack_00000008[2] * in_stack_0000000c[1];
  local_2c = in_stack_00000008[2] * *in_stack_0000000c - in_stack_0000000c[2] * *in_stack_00000008;
  local_28 = in_stack_0000000c[1] * *in_stack_00000008 - *in_stack_0000000c * in_stack_00000008[1];
  fVar1 = SQRT(local_28 * local_28 + local_2c * local_2c + local_30 * local_30);
  psVar2 = (short *)CONCAT22((short)((uint)in_EAX >> 0x10),
                             (ushort)(fVar1 < _DAT_005d856c) << 8 |
                             (ushort)(NAN(fVar1) || NAN(_DAT_005d856c)) << 10 |
                             (ushort)(fVar1 == _DAT_005d856c) << 0xe);
  if ((fVar1 == _DAT_005d856c) == 0) {
    fVar1 = _DAT_005d8568 / fVar1;
    local_30 = local_30 * fVar1;
    local_2c = local_2c * fVar1;
    local_28 = local_28 * fVar1;
  }
  if ((DAT_00704e48 != 4) && ((in_stack_00000028 != 0 || (DAT_008aa8b4 != 0)))) {
    in_stack_0000000c = (float *)CVBufTexture__GetVertexPtr(&stack0x00000008,4);
    Vec3__SetXYZ();
    *in_stack_00000008 = local_20;
    in_stack_00000008[1] = local_1c;
    in_stack_00000008[2] = local_18;
    in_stack_00000008[7] = in_stack_00000018;
    in_stack_00000008[8] = in_stack_0000001c;
    Vec3__SetXYZ();
    Vec3__SetXYZ();
    in_stack_00000008[9] = local_10;
    in_stack_00000008[10] = local_c;
    in_stack_00000008[0xb] = local_8;
    in_stack_00000008[0x10] = in_stack_00000020;
    in_stack_00000008[0x11] = in_stack_0000001c;
    Vec3__SetXYZ();
    Vec3__SetXYZ();
    in_stack_00000008[0x12] = local_20;
    in_stack_00000008[0x13] = local_1c;
    in_stack_00000008[0x14] = local_18;
    in_stack_00000008[0x19] = in_stack_00000020;
    in_stack_00000008[0x1a] = in_stack_00000024;
    Vec3__SetXYZ();
    Vec3__SetXYZ();
    in_stack_00000008[0x1b] = local_20;
    in_stack_00000008[0x1c] = local_1c;
    in_stack_00000008[0x1d] = local_18;
    in_stack_00000008[0x22] = in_stack_00000018;
    in_stack_00000008[0x23] = in_stack_00000024;
    in_stack_00000008[6] = in_stack_00000010;
    in_stack_00000008[0xf] = in_stack_00000010;
    in_stack_00000008[0x18] = in_stack_00000010;
    in_stack_00000008[0x21] = in_stack_00000010;
    CUnitAI__Unk_004c7d90(in_stack_00000008 + 3,&local_30,unaff_EBX);
    CUnitAI__Unk_004c7d90(in_stack_00000008 + 0xc,&local_30,unaff_EBX);
    CUnitAI__Unk_004c7d90(in_stack_00000008 + 0x15,&local_30,unaff_EBX);
    CUnitAI__Unk_004c7d90(in_stack_00000008 + 0x1e,&local_30,unaff_EBX);
    psVar2 = (short *)CVBufTexture__GetIndexPtr(6);
    sVar3 = (short)in_stack_0000000c;
    *psVar2 = sVar3;
    psVar2[5] = sVar3;
    psVar2[1] = sVar3 + 1;
    psVar2[2] = sVar3 + 2;
    psVar2[3] = sVar3 + 2;
    psVar2[4] = sVar3 + 3;
  }
  return (int)psVar2;
}
