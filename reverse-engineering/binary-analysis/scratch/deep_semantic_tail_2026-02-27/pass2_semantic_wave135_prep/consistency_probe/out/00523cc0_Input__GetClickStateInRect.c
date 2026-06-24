/* address: 0x00523cc0 */
/* name: Input__GetClickStateInRect */
/* signature: uint __cdecl Input__GetClickStateInRect(float param_1, float param_2, float param_3, float param_4) */


uint __cdecl Input__GetClickStateInRect(float param_1,float param_2,float param_3,float param_4)

{
  float fVar1;
  uint uVar2;
  undefined2 uVar3;
  ushort uVar4;

  if (DAT_00889008 != (code *)0x0) {
    uVar2 = (*DAT_00889008)(0,4);
    if ((char)uVar2 != '\0') goto LAB_00523d2f;
  }
  uVar2 = g_bDevModeEnabled;
  if ((g_bDevModeEnabled != 0) || (uVar2 = 0, DAT_0089bdfc == 0)) goto LAB_00523d2f;
  fVar1 = (float)DAT_0089bda8;
  uVar4 = (ushort)(fVar1 < param_1) << 8 | (ushort)(NAN(fVar1) || NAN(param_1)) << 10 |
          (ushort)(fVar1 == param_1) << 0xe;
  uVar3 = (undefined2)((uint)DAT_0089bdfc >> 0x10);
  if (fVar1 >= param_1) {
    uVar2 = CONCAT22(uVar3,(ushort)(fVar1 < param_3) << 8 |
                           (ushort)(NAN(fVar1) || NAN(param_3)) << 10 |
                           (ushort)(fVar1 == param_3) << 0xe);
    if (fVar1 >= param_3) goto LAB_00523d2f;
    fVar1 = (float)DAT_0089bda4;
    uVar4 = (ushort)(fVar1 < param_2) << 8 | (ushort)(NAN(fVar1) || NAN(param_2)) << 10 |
            (ushort)(fVar1 == param_2) << 0xe;
    if (fVar1 >= param_2) {
      uVar2 = CONCAT22(uVar3,(ushort)(fVar1 < param_4) << 8 |
                             (ushort)(NAN(fVar1) || NAN(param_4)) << 10 |
                             (ushort)(fVar1 == param_4) << 0xe);
      if (fVar1 < param_4) {
        DAT_0089bdfc = 0;
        return CONCAT31((int3)(uVar2 >> 8),1);
      }
      goto LAB_00523d2f;
    }
  }
  uVar2 = CONCAT22(uVar3,uVar4);
LAB_00523d2f:
  return uVar2 & 0xffffff00;
}
