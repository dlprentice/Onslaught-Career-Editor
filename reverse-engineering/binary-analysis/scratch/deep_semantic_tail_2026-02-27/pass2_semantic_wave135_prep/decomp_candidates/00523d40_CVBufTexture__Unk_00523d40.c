/* address: 0x00523d40 */
/* name: CVBufTexture__Unk_00523d40 */
/* signature: uint __cdecl CVBufTexture__Unk_00523d40(float param_1, float param_2, float param_3, float param_4) */


uint __cdecl CVBufTexture__Unk_00523d40(float param_1,float param_2,float param_3,float param_4)

{
  float fVar1;
  uint uVar2;
  ushort uVar3;

  if (DAT_00889008 != (code *)0x0) {
    uVar2 = (*DAT_00889008)(0,4);
    if ((char)uVar2 != '\0') goto LAB_00523dac;
  }
  uVar2 = g_bDevModeEnabled;
  if ((g_bDevModeEnabled != 0) || (uVar2 = 0, DAT_0089bdf4 == '\0')) goto LAB_00523dac;
  fVar1 = (float)DAT_0089bda8;
  uVar3 = (ushort)(fVar1 < param_1) << 8 | (ushort)(NAN(fVar1) || NAN(param_1)) << 10 |
          (ushort)(fVar1 == param_1) << 0xe;
  if (fVar1 >= param_1) {
    uVar2 = (uint)(ushort)((ushort)(fVar1 < param_3) << 8 |
                           (ushort)(NAN(fVar1) || NAN(param_3)) << 10 |
                          (ushort)(fVar1 == param_3) << 0xe);
    if (fVar1 >= param_3) goto LAB_00523dac;
    fVar1 = (float)DAT_0089bda4;
    uVar3 = (ushort)(fVar1 < param_2) << 8 | (ushort)(NAN(fVar1) || NAN(param_2)) << 10 |
            (ushort)(fVar1 == param_2) << 0xe;
    if (fVar1 >= param_2) {
      uVar3 = (ushort)(fVar1 < param_4) << 8 | (ushort)(NAN(fVar1) || NAN(param_4)) << 10 |
              (ushort)(fVar1 == param_4) << 0xe;
      uVar2 = (uint)uVar3;
      if (fVar1 < param_4) {
        DAT_0089bdf4 = 0;
        return CONCAT31((uint3)(byte)(uVar3 >> 8),1);
      }
      goto LAB_00523dac;
    }
  }
  uVar2 = (uint)uVar3;
LAB_00523dac:
  return uVar2 & 0xffffff00;
}
