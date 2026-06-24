/* address: 0x0046c430 */
/* name: CGame__InitRestartLoop */
/* signature: int __fastcall CGame__InitRestartLoop(void * this) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* Source-aligned mapping to CGame::InitRestartLoop(). Initializes per-level/restart runtime state:
   resets cameras/controllers/objective arrays, initializes EVENT_MANAGER/particles/interface/render
   queue, allocates runtime UI objects (message box/log/pause/help/briefing/random stream),
   registers console commands/CVars, and seeds initial PRE_RUNNING event state. */

int __fastcall CGame__InitRestartLoop(void *this)

{
  int iVar1;
  undefined4 *puVar2;
  void *pvVar3;
  undefined4 extraout_EAX;
  undefined4 extraout_EAX_00;
  undefined4 extraout_EAX_01;
  undefined4 uVar4;
  int unaff_EDI;
  undefined4 *puVar5;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d28db;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  CConsole__Unk_0042d310();
  CDXLandscape__ResetCameraPosition();
  CHud__Unk_004815c0(0x8aa4e8);
  *(undefined4 *)((int)this + 0x3a8) = 0x3d4ccccd;
  *(undefined4 *)((int)this + 0xf4) = 0;
  *(undefined4 *)((int)this + 0xec) = 0x40400000;
  *(undefined4 *)((int)this + 0xc) = 0xbf800000;
  *(undefined4 *)((int)this + 0x48) = 0xbf800000;
  *(undefined1 *)((int)this + 0x38) = 1;
  *(undefined4 *)((int)this + 0xf0) = 0x40400000;
  *(undefined4 *)((int)this + 0x10) = 0;
  *(undefined4 *)((int)this + 0x100) = 0;
  *(undefined4 *)((int)this + 8) = 0;
  *(undefined4 *)((int)this + 0x14) = 0;
  *(undefined4 *)((int)this + 0x298) = 0x3f800000;
  *(undefined4 *)((int)this + 0x20) = 1;
  *(undefined4 *)((int)this + 0x394) = 0;
  *(undefined4 *)((int)this + 0x2e4) = 0;
  *(undefined4 *)((int)this + 0x2e8) = 0;
  puVar2 = (undefined4 *)((int)this + 0x308);
  iVar1 = 0x2408;
  do {
    puVar5 = (undefined4 *)((int)&CAREER + iVar1);
    iVar1 = iVar1 + 4;
    *puVar2 = *puVar5;
    puVar2 = puVar2 + 1;
  } while (iVar1 < 0x2488);
  puVar2 = (undefined4 *)((int)this + 0x2a4);
  iVar1 = 4;
  do {
    puVar2[8] = 0;
    *puVar2 = 0;
    puVar2[0x1cb] = 0;
    puVar2[4] = 0;
    puVar2 = puVar2 + 1;
    iVar1 = iVar1 + -1;
  } while (iVar1 != 0);
  *(undefined4 *)((int)this + 0x40) = 0;
  *(undefined4 *)((int)this + 0x3c) = 0;
  *(undefined4 *)((int)this + 0x3b8) = 0;
  *(undefined4 *)((int)this + 0x3bc) = 0;
  *(undefined4 *)((int)this + 0x304) = 0;
  *(undefined4 *)((int)this + 0x114) = 0;
  *(undefined4 *)((int)this + 0x44) = 0;
  *(undefined4 *)((int)this + 0x4c) = 0;
  *(undefined4 *)((int)this + 0x50) = 0xffffffff;
  puVar2 = (undefined4 *)((int)this + 0x4c);
  puVar5 = (undefined4 *)((int)this + 0x54);
  for (iVar1 = 0x12; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar5 = *puVar2;
    puVar2 = puVar2 + 1;
    puVar5 = puVar5 + 1;
  }
  *(undefined4 *)((int)this + 0x9c) = 0;
  *(undefined4 *)((int)this + 0xa0) = 0xffffffff;
  puVar2 = (undefined4 *)((int)this + 0x9c);
  puVar5 = (undefined4 *)((int)this + 0xa4);
  for (iVar1 = 0x12; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar5 = *puVar2;
    puVar2 = puVar2 + 1;
    puVar5 = puVar5 + 1;
  }
  *(undefined4 *)((int)this + 0x34) = 0;
  CUnitAI__Unk_00441e40(&DAT_0066ffb0);
  CEventManager__Init(&EVENT_MANAGER);
  DAT_009c6400 = 0;
  DAT_009c63f4 = 0;
  DAT_009c63f0 = 0;
  _DAT_009c6404 = 0;
  CMapWho__Init();
  CGameInterface__Unk_004729e0(0x679fa8);
  CDXEngine__InitConsoleVar_UseRenderQueue(&DAT_009c7490);
  CScriptEventNB__CreateEventListener();
  *(undefined4 *)((int)this + 0x2c) = 0;
  *(undefined4 *)((int)this + 0x28) = 1;
  CEventManager__AddEvent_TimeFromNow
            (&EVENT_MANAGER,(float *)((int)this + 0xec),0x7d1,this,0,(void *)0x0,(void *)0x0);
  *(undefined4 *)((int)this + 0x9cc) = 0;
  *(undefined4 *)((int)this + 0x9fc) = 0xffffffff;
  *(undefined4 *)((int)this + 0xa00) = 0xffffffff;
  pvVar3 = (void *)OID__AllocObject(0x800c,0x2b,s_C__dev_ONSLAUGHT2_game_cpp_0062bba4,0x1f9);
  local_4 = 0;
  if (pvVar3 == (void *)0x0) {
    iVar1 = 0;
  }
  else {
    iVar1 = CFearGrid__ctor_like_0044c3d0(pvVar3,(void *)0x0,unaff_EDI);
  }
  local_4 = 0xffffffff;
  *(int *)((int)this + 0x2e4) = iVar1;
  pvVar3 = (void *)OID__AllocObject(0x800c,0x2b,s_C__dev_ONSLAUGHT2_game_cpp_0062bba4,0x1fa);
  local_4 = 1;
  if (pvVar3 == (void *)0x0) {
    iVar1 = 0;
  }
  else {
    iVar1 = CFearGrid__ctor_like_0044c3d0(pvVar3,(void *)0x1,unaff_EDI);
  }
  local_4 = 0xffffffff;
  *(int *)((int)this + 0x2e8) = iVar1;
  pvVar3 = (void *)OID__AllocObject(0x2c8,0x29,s_C__dev_ONSLAUGHT2_game_cpp_0062bba4,0x1fb);
  local_4 = 2;
  if (pvVar3 == (void *)0x0) {
    iVar1 = 0;
  }
  else {
    iVar1 = CMonitor__ctor_like_004b71e0(pvVar3);
  }
  local_4 = 0xffffffff;
  *(int *)((int)this + 0x2ec) = iVar1;
  pvVar3 = (void *)OID__AllocObject(0x40,0x2a,s_C__dev_ONSLAUGHT2_game_cpp_0062bba4,0x1fc);
  local_4 = 3;
  if (pvVar3 == (void *)0x0) {
    iVar1 = 0;
  }
  else {
    iVar1 = CGameMenu__ctor_like_004b8dd0(pvVar3);
  }
  local_4 = 0xffffffff;
  *(int *)((int)this + 0x2f0) = iVar1;
  pvVar3 = (void *)OID__AllocObject(0x4c,0x2a,s_C__dev_ONSLAUGHT2_game_cpp_0062bba4,0x1fd);
  local_4 = 4;
  if (pvVar3 == (void *)0x0) {
    uVar4 = 0;
  }
  else {
    PauseMenu__Init(pvVar3);
    uVar4 = extraout_EAX;
  }
  local_4 = 0xffffffff;
  *(undefined4 *)((int)this + 0x2f4) = uVar4;
  pvVar3 = (void *)OID__AllocObject(0x1c,0x78,s_C__dev_ONSLAUGHT2_game_cpp_0062bba4,0x1ff);
  local_4 = 5;
  if (pvVar3 == (void *)0x0) {
    uVar4 = 0;
  }
  else {
    CHelpTextDisplay__ctor_like_0047fab0(pvVar3);
    uVar4 = extraout_EAX_00;
  }
  local_4 = 0xffffffff;
  *(undefined4 *)((int)this + 0x2f8) = uVar4;
  pvVar3 = (void *)OID__AllocObject(0x14,0x2a,s_C__dev_ONSLAUGHT2_game_cpp_0062bba4,0x200);
  local_4 = 6;
  if (pvVar3 == (void *)0x0) {
    iVar1 = 0;
  }
  else {
    iVar1 = CLevelBriefingLog__ctor_like_0048f540(pvVar3);
  }
  local_4 = 0xffffffff;
  *(int *)((int)this + 0x2fc) = iVar1;
  pvVar3 = (void *)OID__AllocObject(8,0x80,s_C__dev_ONSLAUGHT2_game_cpp_0062bba4,0x201);
  local_4 = 7;
  if (pvVar3 == (void *)0x0) {
    uVar4 = 0;
  }
  else {
    RandomSeedPair__Set(pvVar3,0x1e240);
    uVar4 = extraout_EAX_01;
  }
  local_4 = 0xffffffff;
  *(undefined4 *)((int)this + 0x304) = uVar4;
  CConsole__RegisterCommand
            (s_RemoteCameraOn_0062bec4,s_Set_a_remote_camera_on_the_thing_0062bed4,
             con_remotecameraon,0);
  CConsole__RegisterCommand
            (s_RemoteCameraOff_0062be98,s_Turn_off_the_remote_camera_0062bea8,con_remotecameraoff,0)
  ;
  CConsole__RegisterCommand(&PTR_DAT_0062be84,s_Win_this_level_0062be88,con_win,0);
  CConsole__RegisterCommand(&DAT_0062be6c,s_Lose_this_level_0062be74,con_lose,0);
  CConsole__RegisterCommand(&PTR_DAT_0062be5c,s_Change_map_0062be60,con_map,0);
  CConsole__RegisterCommand
            (s_DumpTextures_0062be24,s_Dumps_all_the_dynamic_textures_t_0062be34,con_dumptextures,0)
  ;
  CConsole__RegisterCommand
            (s_NavMapOn_0062bdfc,s_Turn_the_navigation_map_on_0062be08,con_navmapon,0);
  CConsole__RegisterCommand
            (s_NavMapOff_0062bdd4,s_Turn_the_navigation_map_off_0062bde0,con_navmapoff,0);
  CConsole__RegisterCommand
            (s_ResetMemSizes_0062bd98,s_Resets_the_baseline_for_the_memo_0062bda8,con_resetmemsizes,
             0);
  CConsole__RegisterVariable
            (s_cg_horizontalsplitscreen_0062bd50,s_Is_split_screen_mode_horizontal_o_0062bd6c,3,
             (undefined1 *)((int)this + 0x38),0,0);
  CConsole__RegisterVariable
            (s_cg_interleavedsplitscreen_0062bd10,s_Is_split_screen_mode_interleaved_0062bd2c,3,
             (undefined4 *)((int)this + 0x3c),0,0);
  CConsole__RegisterVariable
            (s_cg_fullscreenmultiplayer_0062bcd4,s_Show_only_player_1_fullscreen_0062bcf0,3,
             (int)this + 0x40,0,0);
  CConsole__RegisterVariable
            (s_g_framelength_0062bca0,s_Game_frame_tick_length__seconds__0062bcb0,4,
             (undefined4 *)((int)this + 0x3a8),0,0);
  puVar2 = &DAT_009c405c;
  puVar5 = &DAT_008a9e58;
  for (iVar1 = 0x81; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar5 = *puVar2;
    puVar2 = puVar2 + 1;
    puVar5 = puVar5 + 1;
  }
  CController__Unk_0042da00(1);
  ExceptionList = local_c;
  return 1;
}
