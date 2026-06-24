/* address: 0x00524180 */
/* name: CVBufTexture__Unk_00524180 */
/* signature: int __thiscall CVBufTexture__Unk_00524180(void * this, void * param_1, void * param_2, uint param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall CVBufTexture__Unk_00524180(void *this,void *param_1,void *param_2,uint param_3)

{
  undefined2 *puVar1;
  int iVar2;
  uint uVar3;
  undefined4 *puVar4;
  void *pvVar5;
  float *pfVar6;
  uint uVar7;
  undefined4 *puVar8;
  int local_c;
  int local_8;

  local_c = 0;
  if ((*(int *)((int)this + 0x22ec) != 0) && (*(int *)((int)this + 0x22ec) == 2)) goto LAB_00524397;
  ogg_sync_init((int)this + 0x2014);
  do {
    iVar2 = CVBufTexture__Unk_00523df0((int)this);
    if (iVar2 == -1) {
      return -1;
    }
    if (iVar2 == 1) {
      ogg_sync_clear((int)this + 0x2014);
      DebugTrace(s_Done__006401b8);
      *(undefined4 *)((int)this + 0x22ec) = 0;
      fclose(*(void **)((int)this + 0x2008));
      *(undefined4 *)((int)this + 0x2008) = 0;
      return local_c;
    }
    while (*(int *)((int)this + 0x22e0) == 0) {
      while( true ) {
        if (*(int *)((int)this + 0x22e0) != 0) goto LAB_0052450f;
        iVar2 = ogg_sync_pageout((int)this + 0x2014,(int)this + 0x2198);
        *(int *)((int)this + 0x22e8) = iVar2;
        if (iVar2 == 0) break;
        if (iVar2 < 0) {
          DebugTrace(s_Corrupt_or_missing_data_in_bitst_006401c0);
        }
        else {
          ogg_stream_pagein((int)this + 0x2030,(int)this + 0x2198);
          while( true ) {
            iVar2 = ogg_stream_packetout((int)this + 0x2030,(int)this + 0x21a8);
            *(int *)((int)this + 0x22e8) = iVar2;
            if (iVar2 == 0) break;
            if (-1 < iVar2) {
              iVar2 = vorbis_synthesis((int)this + 0x2268,(int)this + 0x21a8);
              if (iVar2 == 0) {
                vorbis_synthesis_blockin((int)this + 0x21f8,(int)this + 0x2268);
              }
              while (uVar3 = vorbis_synthesis_pcmout((int)this + 0x21f8,(int)this + 0x22dc),
                    0 < (int)uVar3) {
                if ((int)*(uint *)((int)this + 0x2004) < (int)uVar3) {
                  uVar3 = *(uint *)((int)this + 0x2004);
                }
                uVar7 = *(uint *)((int)this + 0x21cc);
                pvVar5 = (void *)(uVar7 * uVar3 * 2);
                if (pvVar5 < param_2 || (int)pvVar5 - (int)param_2 == 0) {
LAB_005242ca:
                  *(undefined4 *)((int)this + 0x22e4) = 0;
                  if (0 < (int)uVar7) {
                    do {
                      puVar1 = (undefined2 *)((int)this + *(int *)((int)this + 0x22e4) * 2 + 4);
                      pfVar6 = *(float **)
                                (*(int *)((int)this + 0x22dc) + *(int *)((int)this + 0x22e4) * 4);
                      for (uVar7 = uVar3; uVar7 != 0; uVar7 = uVar7 - 1) {
                        local_8 = (int)(longlong)ROUND(*pfVar6 * _DAT_005de7a4);
                        if (local_8 < 0x8000) {
                          if (local_8 < -0x8000) {
                            local_8 = -0x8000;
                          }
                        }
                        else {
                          local_8 = 0x7fff;
                        }
                        *puVar1 = (short)local_8;
                        pfVar6 = pfVar6 + 1;
                        puVar1 = puVar1 + *(int *)((int)this + 0x21cc);
                      }
                      iVar2 = *(int *)((int)this + 0x22e4) + 1;
                      *(int *)((int)this + 0x22e4) = iVar2;
                    } while (iVar2 < *(int *)((int)this + 0x21cc));
                  }
                  vorbis_synthesis_read((int)this + 0x21f8,uVar3);
                  *(uint *)((int)this + 0x22d8) = *(int *)((int)this + 0x21cc) * uVar3 * 2;
                  *(undefined4 *)((int)this + 0x22ec) = 2;
                }
                else {
                  if (param_2 != (void *)0x0) {
                    uVar3 = ((uint)param_2 >> 1) / uVar7;
                    goto LAB_005242ca;
                  }
                  *(undefined4 *)((int)this + 0x22d8) = 0;
                  *(undefined4 *)((int)this + 0x22ec) = 2;
                }
LAB_00524397:
                pvVar5 = *(void **)((int)this + 0x22d8);
                if (param_2 <= pvVar5) {
                  puVar4 = (undefined4 *)((int)this + 4);
                  for (uVar3 = (uint)param_2 >> 2; uVar3 != 0; uVar3 = uVar3 - 1) {
                    *(undefined4 *)param_1 = *puVar4;
                    puVar4 = puVar4 + 1;
                    param_1 = (undefined4 *)((int)param_1 + 4);
                  }
                  for (uVar3 = (uint)param_2 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
                    *(undefined1 *)param_1 = *(undefined1 *)puVar4;
                    puVar4 = (undefined4 *)((int)puVar4 + 1);
                    param_1 = (undefined4 *)((int)param_1 + 1);
                  }
                  uVar3 = *(int *)((int)this + 0x22d8) - (int)param_2;
                  if (uVar3 != 0) {
                    CDXTexture__Helper_0055ed50
                              ((undefined4 *)((int)this + 4),
                               (void *)((int)this + (int)param_2 * 2 + 4),uVar3);
                  }
                  *(int *)((int)this + 0x22d8) = *(int *)((int)this + 0x22d8) - (int)param_2;
                  return local_c + (int)param_2;
                }
                if (pvVar5 != (void *)0x0) {
                  puVar8 = param_1;
                  puVar4 = this;
                  for (uVar3 = (uint)pvVar5 >> 2; puVar4 = puVar4 + 1, uVar3 != 0; uVar3 = uVar3 - 1
                      ) {
                    *puVar8 = *puVar4;
                    puVar8 = puVar8 + 1;
                  }
                  for (uVar3 = (uint)pvVar5 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
                    *(undefined1 *)puVar8 = *(undefined1 *)puVar4;
                    puVar4 = (undefined4 *)((int)puVar4 + 1);
                    puVar8 = (undefined4 *)((int)puVar8 + 1);
                  }
                }
                iVar2 = *(int *)((int)this + 0x22d8);
                param_2 = (void *)((int)param_2 - iVar2);
                param_1 = (void *)((int)param_1 + iVar2);
                local_c = local_c + iVar2;
                *(undefined4 *)((int)this + 0x22d8) = 0;
              }
            }
          }
          iVar2 = ogg_page_eos((int)this + 0x2198);
          if (iVar2 != 0) {
            *(undefined4 *)((int)this + 0x22e0) = 1;
          }
        }
      }
      if (*(int *)((int)this + 0x22e0) != 0) break;
      puVar4 = (undefined4 *)ogg_sync_buffer((int)this + 0x2014,0x1000);
      if (*(void **)((int)this + 0x2008) == (void *)0x0) {
        uVar3 = *(uint *)((int)this + 0x2010);
        if (0xfff < (int)uVar3) {
          uVar3 = 0x1000;
        }
        puVar8 = *(undefined4 **)((int)this + 0x200c);
        for (uVar7 = uVar3 >> 2; uVar7 != 0; uVar7 = uVar7 - 1) {
          *puVar4 = *puVar8;
          puVar8 = puVar8 + 1;
          puVar4 = puVar4 + 1;
        }
        for (uVar7 = uVar3 & 3; uVar7 != 0; uVar7 = uVar7 - 1) {
          *(undefined1 *)puVar4 = *(undefined1 *)puVar8;
          puVar8 = (undefined4 *)((int)puVar8 + 1);
          puVar4 = (undefined4 *)((int)puVar4 + 1);
        }
        *(uint *)((int)this + 0x2010) = *(int *)((int)this + 0x2010) - uVar3;
        *(uint *)((int)this + 0x200c) = *(int *)((int)this + 0x200c) + uVar3;
      }
      else {
        uVar3 = fread(puVar4,1,0x1000,*(void **)((int)this + 0x2008));
      }
      ogg_sync_wrote((int)this + 0x2014,uVar3);
      if (uVar3 == 0) {
        *(undefined4 *)((int)this + 0x22e0) = 1;
      }
    }
LAB_0052450f:
    ogg_stream_clear((int)this + 0x2030);
    vorbis_block_clear((int)this + 0x2268);
    vorbis_dsp_clear((int)this + 0x21f8);
    vorbis_comment_clear((int)this + 0x21e8);
    vorbis_info_clear((int)this + 0x21c8);
  } while( true );
}
