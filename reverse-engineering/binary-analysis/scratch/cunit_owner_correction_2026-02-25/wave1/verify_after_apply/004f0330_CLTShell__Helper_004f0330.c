/* address: 0x004f0330 */
/* name: CLTShell__Helper_004f0330 */
/* signature: int __fastcall CLTShell__Helper_004f0330(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CLTShell__Helper_004f0330(void *param_1)

{
  int aLevel;
  int iVar1;
  int iVar2;
  int aLevel_00;
  uint arg2;

  if (0 < DAT_00663058) {
    CUnit__Unk_004f0200(DAT_00663058);
  }
  iVar2 = DAT_00662dc8;
  aLevel_00 = 0;
  if (DAT_00662dc8 == -1) {
    while( true ) {
      if (aLevel_00 == -0x45) {
        arg2 = 2;
      }
      else {
        arg2 = (uint)(aLevel_00 == -3);
      }
      if (DAT_0083d44c != '\0') {
        DAT_0083d44c = '\0';
        arg2 = 0;
      }
      CDXEngine__Unk_00549310();
      aLevel_00 = CFrontEnd__Run(&DAT_0089d758,arg2,1);
      CDXEngine__Unk_00549310();
      CDXEngine__Unk_005492d0(0x9c3df0);
      if (0 < DAT_00663058) {
        CUnit__Unk_004f0200(DAT_00663058);
      }
      if (aLevel_00 == -1) break;
      if (aLevel_00 == -3) {
        DAT_00662f3c = 1;
        if (DAT_0066e94e == '\0') {
          DAT_0083d3ec = CTexture__FindTexture(s_splash_tga_00632bcc,0,0,1,1,1);
          DAT_00662f3c = 0;
        }
        else {
          DAT_0083d3ec = CTexture__FindTexture(s_vectorlosttoyssplash_tga_00632bd8,0,0,1,1,1);
        }
        _DAT_0083d450 = 0;
        DebugTrace(s_Considering_doing_fmvs____00632bb0);
        DebugTrace(s_we_re_in_attract_mode_00632b98);
        iVar2 = CFrontEnd__Unk_00465640();
        if ((iVar2 == 0) && ((DAT_0083d404 == 0 || (iVar2 = CFrontEnd__Unk_00465640(), iVar2 == 0)))
           ) {
          DAT_00650610 = 0x78e;
          CFrontEnd__Unk_00465640();
          DAT_00650610 = 0x7fffffff;
        }
        if (DAT_0083d3ec != (int *)0x0) {
          CUnit__Unk_004f27e0((int)(DAT_0083d3ec + 2));
          CTexture__Release(DAT_0083d3ec);
        }
      }
      else {
        CDXEngine__Unk_00549310();
        iVar2 = CGame__RunLevel(&DAT_008a9a98,aLevel_00);
        CDXEngine__Unk_00549310();
        CDXEngine__Unk_005492d0(0x9c3df0);
        if (iVar2 == 5) {
          aLevel_00 = -3;
        }
        else if (iVar2 == 7) {
          aLevel_00 = -0x45;
        }
      }
    }
  }
  else {
    *(int *)param_1 = DAT_00662dc8;
    do {
      aLevel = *(int *)param_1;
      if (aLevel == -1) {
        *(int *)param_1 = iVar2;
        return 0;
      }
      *(undefined4 *)param_1 = 0xffffffff;
      iVar1 = CGame__RunLevel(&DAT_008a9a98,aLevel);
      iVar2 = aLevel;
    } while (iVar1 != 2);
  }
  return aLevel_00;
}
