/* address: 0x00523df0 */
/* name: CVBufTexture__Unk_00523df0 */
/* signature: int __fastcall CVBufTexture__Unk_00523df0(int param_1) */


int __fastcall CVBufTexture__Unk_00523df0(int param_1)

{
  int *piVar1;
  undefined4 *puVar2;
  uint uVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  uint uVar7;
  undefined4 *puVar8;
  int *piVar9;
  char *pcVar10;

  *(undefined4 *)(param_1 + 0x22e0) = 0;
  puVar2 = (undefined4 *)ogg_sync_buffer(param_1 + 0x2014,0x1000);
  if (*(void **)(param_1 + 0x2008) == (void *)0x0) {
    uVar3 = *(uint *)(param_1 + 0x2010);
    if (0xfff < (int)uVar3) {
      uVar3 = 0x1000;
    }
    puVar8 = *(undefined4 **)(param_1 + 0x200c);
    for (uVar7 = uVar3 >> 2; uVar7 != 0; uVar7 = uVar7 - 1) {
      *puVar2 = *puVar8;
      puVar8 = puVar8 + 1;
      puVar2 = puVar2 + 1;
    }
    for (uVar7 = uVar3 & 3; uVar7 != 0; uVar7 = uVar7 - 1) {
      *(undefined1 *)puVar2 = *(undefined1 *)puVar8;
      puVar8 = (undefined4 *)((int)puVar8 + 1);
      puVar2 = (undefined4 *)((int)puVar2 + 1);
    }
    *(uint *)(param_1 + 0x2010) = *(int *)(param_1 + 0x2010) - uVar3;
    *(uint *)(param_1 + 0x200c) = *(int *)(param_1 + 0x200c) + uVar3;
  }
  else {
    uVar3 = fread(puVar2,1,0x1000,*(void **)(param_1 + 0x2008));
  }
  ogg_sync_wrote(param_1 + 0x2014,uVar3);
  iVar6 = param_1 + 0x2198;
  iVar4 = ogg_sync_pageout(param_1 + 0x2014,iVar6);
  if (iVar4 != 1) {
    if (0xfff < (int)uVar3) {
      DebugTrace(s_Input_does_not_appear_to_be_an_O_00640188);
      return -1;
    }
    return 1;
  }
  iVar4 = param_1 + 0x2030;
  uVar5 = ogg_page_serialno(iVar6);
  ogg_stream_init(iVar4,uVar5);
  vorbis_info_init(param_1 + 0x21c8);
  vorbis_comment_init(param_1 + 0x21e8);
  iVar6 = ogg_stream_pagein(iVar4,iVar6);
  if (iVar6 < 0) {
    DebugTrace(s_Error_reading_first_page_of_Ogg_b_00640154);
    return -1;
  }
  iVar6 = ogg_stream_packetout(iVar4,param_1 + 0x21a8);
  if (iVar6 != 1) {
    DebugTrace(s_Error_reading_initial_header_pac_0064012c);
    return -1;
  }
  iVar6 = vorbis_synthesis_headerin(param_1 + 0x21c8,param_1 + 0x21e8,param_1 + 0x21a8);
  if (iVar6 < 0) {
    DebugTrace(s_This_Ogg_bitstream_does_not_cont_006400f4);
    return -1;
  }
  *(undefined4 *)(param_1 + 0x22e4) = 0;
  do {
    iVar6 = *(int *)(param_1 + 0x22e4);
    while (iVar6 < 2) {
      iVar6 = ogg_sync_pageout(param_1 + 0x2014,param_1 + 0x2198);
      *(int *)(param_1 + 0x22e8) = iVar6;
      if (iVar6 == 0) break;
      if (iVar6 == 1) {
        ogg_stream_pagein(param_1 + 0x2030,param_1 + 0x2198);
        if (1 < *(int *)(param_1 + 0x22e4)) break;
        do {
          iVar6 = ogg_stream_packetout(param_1 + 0x2030,param_1 + 0x21a8);
          *(int *)(param_1 + 0x22e8) = iVar6;
          if (iVar6 == 0) break;
          if (iVar6 < 0) {
            DebugTrace(s_Corrupt_secondary_header__Exitin_00640094);
            return -1;
          }
          vorbis_synthesis_headerin(param_1 + 0x21c8,param_1 + 0x21e8,param_1 + 0x21a8);
          iVar6 = *(int *)(param_1 + 0x22e4) + 1;
          *(int *)(param_1 + 0x22e4) = iVar6;
        } while (iVar6 < 2);
      }
      iVar6 = *(int *)(param_1 + 0x22e4);
    }
    puVar2 = (undefined4 *)ogg_sync_buffer(param_1 + 0x2014,0x1000);
    if (*(void **)(param_1 + 0x2008) == (void *)0x0) {
      uVar3 = *(uint *)(param_1 + 0x2010);
      if (0xfff < (int)uVar3) {
        uVar3 = 0x1000;
      }
      puVar8 = *(undefined4 **)(param_1 + 0x200c);
      for (uVar7 = uVar3 >> 2; uVar7 != 0; uVar7 = uVar7 - 1) {
        *puVar2 = *puVar8;
        puVar8 = puVar8 + 1;
        puVar2 = puVar2 + 1;
      }
      for (uVar7 = uVar3 & 3; uVar7 != 0; uVar7 = uVar7 - 1) {
        *(undefined1 *)puVar2 = *(undefined1 *)puVar8;
        puVar8 = (undefined4 *)((int)puVar8 + 1);
        puVar2 = (undefined4 *)((int)puVar2 + 1);
      }
      *(uint *)(param_1 + 0x2010) = *(int *)(param_1 + 0x2010) - uVar3;
      *(uint *)(param_1 + 0x200c) = *(int *)(param_1 + 0x200c) + uVar3;
    }
    else {
      uVar3 = fread(puVar2,1,0x1000,*(void **)(param_1 + 0x2008));
    }
    ogg_sync_wrote(param_1 + 0x2014,uVar3);
    if ((uVar3 == 0) && (*(int *)(param_1 + 0x22e4) < 2)) {
      DebugTrace(s_End_of_file_before_finding_all_V_00640064);
      return -1;
    }
    if (1 < *(int *)(param_1 + 0x22e4)) {
      piVar9 = *(int **)(param_1 + 0x21e8);
      iVar6 = *piVar9;
      while (iVar6 != 0) {
        DebugTrace(&DAT_00622dbc);
        piVar1 = piVar9 + 1;
        piVar9 = piVar9 + 1;
        iVar6 = *piVar1;
      }
      DebugTrace(s_Bitstream_is__d_channel___ldHz_006400d0);
      uVar5 = *(undefined4 *)(param_1 + 0x21f4);
      pcVar10 = s_Encoded_by___s_006400bc;
      DebugTrace(s_Encoded_by___s_006400bc);
      *(int *)(param_1 + 0x2004) = (int)(0x1000 / (longlong)*(int *)(param_1 + 0x21cc));
      vorbis_synthesis_init(param_1 + 0x21f8,param_1 + 0x21c8,pcVar10,uVar5);
      vorbis_block_init(param_1 + 0x21f8,param_1 + 0x2268);
      return 0;
    }
  } while( true );
}
