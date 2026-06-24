/* address: 0x00523bc0 */
/* name: Input__DispatchClickInRect */
/* signature: uint __cdecl Input__DispatchClickInRect(float param_1, float param_2, float param_3, float param_4, int param_5) */


uint __cdecl
Input__DispatchClickInRect(float param_1,float param_2,float param_3,float param_4,int param_5)

{
  float fVar1;
  code *pcVar2;
  undefined2 uVar3;
  code *extraout_EAX;
  ushort uVar4;
  int unaff_retaddr;

  if (DAT_00889008 != (code *)0x0) {
    pcVar2 = (code *)(*DAT_00889008)(0,4);
    if ((char)pcVar2 != '\0') goto LAB_00523cbb;
  }
  if (DAT_00889008 == (code *)0x0) {
LAB_00523bf0:
    pcVar2 = g_bDevModeEnabled;
    if ((g_bDevModeEnabled == (code *)0x0) && (pcVar2 = (code *)0x0, DAT_0089bdfc != 0)) {
      fVar1 = (float)DAT_0089bda8;
      uVar4 = (ushort)(fVar1 < param_1) << 8 | (ushort)(NAN(fVar1) || NAN(param_1)) << 10 |
              (ushort)(fVar1 == param_1) << 0xe;
      uVar3 = (undefined2)((uint)DAT_0089bdfc >> 0x10);
      if (fVar1 < param_1 == 0) {
        pcVar2 = (code *)CONCAT22(uVar3,(ushort)(fVar1 < param_3) << 8 |
                                        (ushort)(NAN(fVar1) || NAN(param_3)) << 10 |
                                        (ushort)(fVar1 == param_3) << 0xe);
        if (fVar1 < param_3 != 0) {
          fVar1 = (float)DAT_0089bda4;
          uVar4 = (ushort)(fVar1 < param_2) << 8 | (ushort)(NAN(fVar1) || NAN(param_2)) << 10 |
                  (ushort)(fVar1 == param_2) << 0xe;
          if (fVar1 < param_2 != 0) goto LAB_00523c61;
          pcVar2 = (code *)CONCAT22(uVar3,(ushort)(fVar1 < param_4) << 8 |
                                          (ushort)(NAN(fVar1) || NAN(param_4)) << 10 |
                                          (ushort)(fVar1 == param_4) << 0xe);
          if (fVar1 < param_4 != 0) {
            DAT_0089bdfc = 0;
            VFuncSlot_03_004669a0(&DAT_0089d758,DAT_008a9564,param_5,0x3f800000,unaff_retaddr);
            pcVar2 = extraout_EAX;
          }
        }
      }
      else {
LAB_00523c61:
        pcVar2 = (code *)CONCAT22(uVar3,uVar4);
      }
    }
  }
  else {
    pcVar2 = (code *)(*DAT_00889008)(0,4);
    if ((char)pcVar2 == '\0') goto LAB_00523bf0;
  }
  pcVar2 = (code *)CONCAT31((int3)((uint)pcVar2 >> 8),DAT_0089bdf4);
  if (((DAT_0089bdf4 == '\0') || (pcVar2 = DAT_00889008, DAT_00889008 != (code *)0x0)) ||
     (pcVar2 = g_bDevModeEnabled, g_bDevModeEnabled != (code *)0x0)) goto LAB_00523cbb;
  fVar1 = (float)DAT_0089bda8;
  uVar4 = (ushort)(fVar1 < param_1) << 8 | (ushort)(NAN(fVar1) || NAN(param_1)) << 10 |
          (ushort)(fVar1 == param_1) << 0xe;
  if (fVar1 >= param_1) {
    pcVar2 = (code *)(uint)(ushort)((ushort)(fVar1 < param_3) << 8 |
                                    (ushort)(NAN(fVar1) || NAN(param_3)) << 10 |
                                   (ushort)(fVar1 == param_3) << 0xe);
    if (fVar1 >= param_3) goto LAB_00523cbb;
    fVar1 = (float)DAT_0089bda4;
    uVar4 = (ushort)(fVar1 < param_2) << 8 | (ushort)(NAN(fVar1) || NAN(param_2)) << 10 |
            (ushort)(fVar1 == param_2) << 0xe;
    if (fVar1 >= param_2) {
      uVar4 = (ushort)(fVar1 < param_4) << 8 | (ushort)(NAN(fVar1) || NAN(param_4)) << 10 |
              (ushort)(fVar1 == param_4) << 0xe;
      pcVar2 = (code *)(uint)uVar4;
      if (fVar1 < param_4) {
        return CONCAT31((uint3)(byte)(uVar4 >> 8),1);
      }
      goto LAB_00523cbb;
    }
  }
  pcVar2 = (code *)(uint)uVar4;
LAB_00523cbb:
  return (uint)pcVar2 & 0xffffff00;
}
