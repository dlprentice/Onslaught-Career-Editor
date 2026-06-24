/* address: 0x0043ed80 */
/* name: CCutscene__Load */
/* signature: undefined CCutscene__Load(void) */


undefined4 CCutscene__Load(void)

{
  char cVar1;
  int iVar2;
  int extraout_ECX;
  uint uVar3;
  uint uVar4;
  void *this;
  int unaff_ESI;
  char *pcVar5;
  int unaff_EDI;
  char *pcVar6;
  void *in_stack_00001108;
  void *local_c;
  undefined1 *local_8;
  int local_4;

  local_4 = 0xffffffff;
  local_8 = &LAB_005d200c;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  CDXTexture__Helper_0055def0();
  CConsole__Printf(&DAT_0066f580,s_LOADING_cutscene_____006281e0);
  sprintf(&stack0x00000108,s_data_cutscenes__s_cut_00628144);
  local_4 = ((DAT_0062813f * 0x100 + (int)DAT_0062813e) * 0x100 + (int)DAT_0062813d) * 0x100 +
            (int)DAT_0062813c;
  local_8 = (undefined1 *)OID__AllocObject(0x10,0x1c,s_C__dev_ONSLAUGHT2_Cutscene_cpp_0062811c,0xcb)
  ;
  this = (void *)0x0;
  if (local_8 != (undefined1 *)0x0) {
    this = (void *)CChunker__Create();
  }
  iVar2 = CUnitAI__Unk_004238c0(this,&stack0x00000108,unaff_ESI);
  if (iVar2 == 0) {
    sprintf(&stack0x00000008,s_Error_loading_cutscene_file__s__006281c0);
  }
  uVar3 = 0xffffffff;
  pcVar5 = &DAT_006281b8;
  do {
    pcVar6 = pcVar5;
    if (uVar3 == 0) break;
    uVar3 = uVar3 - 1;
    pcVar6 = pcVar5 + 1;
    cVar1 = *pcVar5;
    pcVar5 = pcVar6;
  } while (cVar1 != '\0');
  uVar3 = ~uVar3;
  pcVar5 = pcVar6 + -uVar3;
  pcVar6 = (char *)(extraout_ECX + 0x73c);
  for (uVar4 = uVar3 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
    *(undefined4 *)pcVar6 = *(undefined4 *)pcVar5;
    pcVar5 = pcVar5 + 4;
    pcVar6 = pcVar6 + 4;
  }
  for (uVar3 = uVar3 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
    *pcVar6 = *pcVar5;
    pcVar5 = pcVar5 + 1;
    pcVar6 = pcVar6 + 1;
  }
  *(undefined4 *)(extraout_ECX + 0x83c) = 5;
  uVar3 = CMeshPart__Helper_00423910((uint)this);
  while (uVar3 != 0) {
    if (uVar3 == ((DAT_00628117 * 0x100 + (int)DAT_00628116) * 0x100 + (int)DAT_00628115) * 0x100 +
                 (int)DAT_00628114) {
      CMeshPart__Helper_00423960(this,(int)&stack0x00000000,4,1,unaff_EDI);
      if (local_4 !=
          ((DAT_0062813f * 0x100 + (int)DAT_0062813e) * 0x100 + (int)DAT_0062813d) * 0x100 +
          (int)DAT_0062813c) {
        DebugTrace(s_Warning__Unknown_cutscene_file_v_0062818c);
      }
    }
    else if (uVar3 == ((DAT_0062810f * 0x100 + (int)DAT_0062810e) * 0x100 + (int)DAT_0062810d) *
                      0x100 + (int)DAT_0062810c) {
      CMeshPart__Helper_00423960(this,extraout_ECX + 0x1c,0x10,1,unaff_EDI);
      CMeshPart__Helper_00423960(this,extraout_ECX + 0x848,4,1,unaff_EDI);
    }
    else if (uVar3 == ((DAT_00628107 * 0x100 + (int)DAT_00628106) * 0x100 + (int)DAT_00628105) *
                      0x100 + (int)DAT_00628104) {
      CMeshPart__Helper_00423960(this,extraout_ECX + 0xf4,4,1,unaff_EDI);
    }
    else if (uVar3 == ((DAT_006280f7 * 0x100 + (int)DAT_006280f6) * 0x100 + (int)DAT_006280f5) *
                      0x100 + (int)DAT_006280f4) {
      CMeshPart__Helper_00423960(this,(int)&local_c,4,1,unaff_EDI);
      CMeshPart__Helper_00423960(this,(int)local_c * 0x20 + 0x170 + extraout_ECX,0x20,1,unaff_EDI);
      CMeshPart__Helper_00423960(this,extraout_ECX + 0xf8 + (int)local_c * 4,4,1,unaff_EDI);
      CMeshPart__Helper_00423960(this,extraout_ECX + 0x530 + (int)local_c * 4,4,1,unaff_EDI);
      CMeshPart__Helper_00423960(this,(int)&stack0x00000004,4,1,unaff_EDI);
    }
    else if (uVar3 == ((DAT_006280ef * 0x100 + (int)DAT_006280ee) * 0x100 + (int)DAT_006280ed) *
                      0x100 + (int)DAT_006280ec) {
      CMeshPart__Helper_00423960(this,(int)&local_8,4,1,unaff_EDI);
      iVar2 = CCutscene__AddAnimation(local_8,&DAT_00662b2c,&DAT_00662b2c,0,0);
      CMeshPart__Helper_00423960(this,iVar2 + 0x108,0x20,1,unaff_EDI);
      CMeshPart__Helper_00423960(this,iVar2 + 0x12d,0x100,1,unaff_EDI);
      CMeshPart__Helper_00423960(this,iVar2 + 0x230,4,1,unaff_EDI);
      CMeshPart__Helper_00423960(this,iVar2 + 8,0x100,1,unaff_EDI);
      CMeshPart__Helper_00423960(this,iVar2,4,1,unaff_EDI);
      CMeshPart__Helper_00423960(this,iVar2 + 0x234,4,1,unaff_EDI);
      CMeshPart__Helper_00423960(this,iVar2 + 0x23c,4,1,unaff_EDI);
      CMeshPart__Helper_00423960(this,iVar2 + 0x240,4,1,unaff_EDI);
    }
    else if (uVar3 == ((DAT_006280ff * 0x100 + (int)DAT_006280fe) * 0x100 + (int)DAT_006280fd) *
                      0x100 + (int)DAT_006280fc) {
      CMeshPart__Helper_00423960(this,extraout_ECX + 0x73c,0x100,1,unaff_EDI);
      CMeshPart__Helper_00423960(this,extraout_ECX + 0x83c,4,1,unaff_EDI);
    }
    else {
      DebugTrace(s_Warning__Unknown_chunk_found_in_c_0062815c);
      CUnitAI__Unk_00423990(this);
    }
    uVar3 = CMeshPart__Helper_00423910((uint)this);
  }
  CUnitAI__Unk_00423900();
  if (this != (void *)0x0) {
    CUnitAI__Unk_00423840((int)this);
    OID__FreeObject(this);
  }
  *(undefined1 *)(extraout_ECX + 0x841) = 1;
  ExceptionList = in_stack_00001108;
  return 1;
}
