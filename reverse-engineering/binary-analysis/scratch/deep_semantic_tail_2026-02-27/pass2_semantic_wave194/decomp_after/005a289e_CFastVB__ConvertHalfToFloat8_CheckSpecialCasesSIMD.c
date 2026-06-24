/* address: 0x005a289e */
/* name: CFastVB__ConvertHalfToFloat8_CheckSpecialCasesSIMD */
/* signature: void CFastVB__ConvertHalfToFloat8_CheckSpecialCasesSIMD(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CFastVB__ConvertHalfToFloat8_CheckSpecialCasesSIMD(void)

{
  ushort in_XMM0_Wa;
  ushort in_XMM0_Wb;
  ushort in_XMM0_Wc;
  ushort in_XMM0_Wd;
  ushort in_XMM0_We;
  ushort in_XMM0_Wf;
  ushort in_XMM0_Wg;
  ushort in_XMM0_Wh;
  undefined1 auVar1 [16];

  auVar1._0_2_ = -(ushort)((_DAT_0065e750 & in_XMM0_Wa) == 0);
  auVar1._2_2_ = -(ushort)((uRam0065e752 & in_XMM0_Wb) == 0);
  auVar1._4_2_ = -(ushort)((uRam0065e754 & in_XMM0_Wc) == 0);
  auVar1._6_2_ = -(ushort)((uRam0065e756 & in_XMM0_Wd) == 0);
  auVar1._8_2_ = -(ushort)((uRam0065e758 & in_XMM0_We) == 0);
  auVar1._10_2_ = -(ushort)((uRam0065e75a & in_XMM0_Wf) == 0);
  auVar1._12_2_ = -(ushort)((uRam0065e75c & in_XMM0_Wg) == 0);
  auVar1._14_2_ = -(ushort)((uRam0065e75e & in_XMM0_Wh) == 0);
  if ((((((((((((((((SUB161(auVar1 >> 7,0) & 1) != 0 || (SUB161(auVar1 >> 0xf,0) & 1) != 0) ||
                  (SUB161(auVar1 >> 0x17,0) & 1) != 0) || (SUB161(auVar1 >> 0x1f,0) & 1) != 0) ||
                (SUB161(auVar1 >> 0x27,0) & 1) != 0) || (SUB161(auVar1 >> 0x2f,0) & 1) != 0) ||
              (SUB161(auVar1 >> 0x37,0) & 1) != 0) || (SUB161(auVar1 >> 0x3f,0) & 1) != 0) ||
            (SUB161(auVar1 >> 0x47,0) & 1) != 0) || (SUB161(auVar1 >> 0x4f,0) & 1) != 0) ||
          (SUB161(auVar1 >> 0x57,0) & 1) != 0) || (SUB161(auVar1 >> 0x5f,0) & 1) != 0) ||
        (SUB161(auVar1 >> 0x67,0) & 1) != 0) || (SUB161(auVar1 >> 0x6f,0) & 1) != 0) ||
      (auVar1._14_2_ >> 7 & 1) != 0) || (auVar1._14_2_ & 0x8000) != 0) {
    return;
  }
  return;
}
