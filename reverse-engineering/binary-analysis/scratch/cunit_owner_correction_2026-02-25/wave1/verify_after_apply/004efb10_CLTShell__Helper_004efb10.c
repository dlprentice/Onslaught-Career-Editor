/* address: 0x004efb10 */
/* name: CLTShell__Helper_004efb10 */
/* signature: int __fastcall CLTShell__Helper_004efb10(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CLTShell__Helper_004efb10(void *param_1)

{
  uint language;
  char cVar1;
  int iVar2;
  char *unaff_EDI;
  bool bVar3;
  undefined1 local_2fc [376];
  undefined1 local_184 [376];
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d503b;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  if (DAT_0082b4a4 == 0) {
    ExceptionList = &local_c;
    CVar__SetValueRounded();
  }
  PLATFORM__GetSysTimeFloat();
  CSPtrSet__Initialise(40000);
  CUnit__Helper_004416e0(0x66f580);
  CUnit__Helper_004416e0(0x66eb90);
  CController__ctor(local_184,&DAT_0089be50,1,1);
  local_4 = 0;
  CController__ctor(local_2fc,&DAT_0089be5c,1,1);
  CController__dtor(local_2fc);
  local_4 = 0xffffffff;
  CController__dtor(local_184);
  CConsole__Init();
  CConsole__Printf(&DAT_0066eb90,s_Console_initialised_00632c40);
  if (DAT_008554a4 == '\0') {
    Controls__ApplyPreset(1);
  }
  iVar2 = PCPlatform__Init();
  if (iVar2 == 0) {
    ExceptionList = local_c;
    return 0;
  }
  PLATFORM__GetSysTimeFloat();
  DebugTrace(s_Platform_init_took__fs_00632c28);
  PLATFORM__GetSysTimeFloat();
  CController__Unk_0042d7a0();
  CDXFMV__VFunc_06_0053f180();
  PLATFORM__GetSysTimeFloat();
  DebugTrace(s_FMV_init_took__fs_00632c14);
  PLATFORM__GetSysTimeFloat();
  if (DAT_00662f40 != 0) {
    CConsole__Printf(&DAT_0066eb90,s_Starting_music_00632c04);
    CConsole__Printf(&DAT_0066eb90,s_Starting_sound_00632bf4);
    cVar1 = CSoundManager__Init();
    if (cVar1 == '\0') {
      DAT_00662f40 = 0;
      DAT_00662dcc = 0;
    }
    CMusic__Init(&DAT_00889a48);
    CConsole__Printf(&DAT_0066eb90,&DAT_0062b13c);
  }
  if (((DAT_00662dc8 != -1) || (DAT_0066304c != -1)) || (DAT_00663050 != 0)) goto LAB_004efeea;
  bVar3 = DAT_006630cc == 0;
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
  if (bVar3) {
    if (DAT_00662f28 == 0) {
      CFrontEnd__Unk_00465640();
      CFrontEnd__Unk_00465640();
      CFrontEnd__Unk_00465640();
      CFrontEnd__Unk_00465640();
    }
    else {
      CFrontEnd__Unk_00465640();
      if (g_bDevModeEnabled == 0) {
        if (DAT_0083d404 != 0) {
          CFrontEnd__Unk_00465640();
        }
        DAT_00650610 = 0x78e;
        _DAT_0083d450 = CFrontEnd__Unk_00465640();
        goto LAB_004efec4;
      }
    }
  }
  else {
    DebugTrace(s_we_re_in_attract_mode_00632b98);
    iVar2 = CFrontEnd__Unk_00465640();
    if ((iVar2 == 0) && ((DAT_0083d404 == 0 || (iVar2 = CFrontEnd__Unk_00465640(), iVar2 == 0)))) {
      DAT_00650610 = 0x78e;
      CFrontEnd__Unk_00465640();
LAB_004efec4:
      DAT_00650610 = 0x7fffffff;
    }
  }
  if (DAT_0083d3ec != (int *)0x0) {
    CUnit__Unk_004f27e0((int)(DAT_0083d3ec + 2));
    CTexture__Release(DAT_0083d3ec);
  }
LAB_004efeea:
  CText__Ctor(&g_Text);
  language = DAT_0066305c;
  if (g_UseAmericanEnglish != 0) {
    language = 0;
  }
  CText__Init(&g_Text,language);
  CFrontEndPage__Init_ReturnTrue();
  if (DAT_00662dd4 == 0) {
    CResourceAccumulator__ReadResourceFile(0xffffffff,0);
  }
  PCPlatform__LoadFonts();
  CConsole__ResetLayoutForWindowHeight(&DAT_00663498);
  CConsole__SetLoading(&DAT_00663498,'\x01',1);
  CConsole__SetLoadingRange(&DAT_00663498,0.0,40.0);
  CConsole__SetLoadingFraction(&DAT_00663498,0.0);
  CConsole__SetLoadingRange(&DAT_00663498,40.0,50.0);
  CConsole__SetLoadingFraction(&DAT_00663498,0.1);
  DebugTrace(unaff_EDI);
  CResourceDescriptorTable__InitDefaultMeshNames();
  CConsole__SetLoadingFraction(&DAT_00663498,0.2);
  CConsole__SetLoadingFraction(&DAT_00663498,0.3);
  if (DAT_0083d3e8 != 0) {
    *(int *)(DAT_0083d3e8 + 0x170) = *(int *)(DAT_0083d3e8 + 0x170) + -1;
    DAT_0083d3e8 = 0;
  }
  DAT_0083d3e8 = CMesh__FindOrCreate(s_default_msh_00632b30);
  CConsole__SetLoadingFraction(&DAT_00663498,0.4);
  if (DAT_0083d3e4 != (int *)0x0) {
    CUnit__Unk_004f27e0((int)DAT_0083d3e4 + 8);
    DAT_0083d3e4 = (int *)0x0;
  }
  DAT_0083d3e4 = CTexture__FindTexture(s_FrontEnd_v2_FE_Blank_tga_00629f68,0,0,1,1,1);
  if (DAT_0083d3e0 != (int *)0x0) {
    CUnit__Unk_004f27e0((int)DAT_0083d3e0 + 8);
    DAT_0083d3e0 = (int *)0x0;
  }
  DAT_0083d3e0 = CTexture__FindTexture(s_loadingscreen_tga_00625338,0,0,1,1,1);
  CConsole__SetLoadingFraction(&DAT_00663498,0.5);
  if (DAT_0083d448 == 0) {
    DebugTrace(unaff_EDI);
  }
  CMesh__InitStatic();
  CConsole__SetLoadingFraction(&DAT_00663498,0.6);
  *(undefined4 *)param_1 = 0xffffffff;
  CWorldPhysicsManager__Unk_00510800();
  CConsole__SetLoadingFraction(&DAT_00663498,1.0);
  CMemoryManager__Unk_004a2a20(&DAT_009c3df0);
  ExceptionList = local_c;
  return 1;
}
