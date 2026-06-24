/* address: 0x004e2c50 */
/* name: CSoundManager__ReloadLanguageSampleBank */
/* signature: void __fastcall CSoundManager__ReloadLanguageSampleBank(void * param_1) */


void __fastcall CSoundManager__ReloadLanguageSampleBank(void *param_1)

{
  char cVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  char *pcVar8;
  char *pcVar9;
  char *b;
  char local_c8 [200];

  b = (char *)((int)param_1 + 0x88);
  if (*(char *)((int)param_1 + 4) != '\0') {
    CText__GetLanguageName(&g_Text);
    sprintf(local_c8,PTR_s__s_data_sounds_sounds__s_pc_xap_0063e2a8);
    iVar5 = stricmp(local_c8,b);
    if (iVar5 != 0) {
      if (b != (char *)0x0) {
        uVar6 = 0xffffffff;
        pcVar8 = local_c8;
        do {
          pcVar9 = pcVar8;
          if (uVar6 == 0) break;
          uVar6 = uVar6 - 1;
          pcVar9 = pcVar8 + 1;
          cVar1 = *pcVar8;
          pcVar8 = pcVar9;
        } while (cVar1 != '\0');
        uVar6 = ~uVar6;
        pcVar8 = pcVar9 + -uVar6;
        for (uVar7 = uVar6 >> 2; uVar7 != 0; uVar7 = uVar7 - 1) {
          *(undefined4 *)b = *(undefined4 *)pcVar8;
          pcVar8 = pcVar8 + 4;
          b = b + 4;
        }
        for (uVar6 = uVar6 & 3; uVar6 != 0; uVar6 = uVar6 - 1) {
          *b = *pcVar8;
          pcVar8 = pcVar8 + 1;
          b = b + 1;
        }
      }
      DebugTrace(s_Loading_XAP_00632628);
      iVar5 = *(int *)((int)param_1 + 0xc);
      while (iVar5 != 0) {
        iVar2 = *(int *)(iVar5 + 0x74);
        if (iVar2 != 0) {
          *(undefined4 *)(iVar2 + 0x78) = *(undefined4 *)(iVar5 + 0x78);
        }
        if (*(int *)(iVar5 + 0x78) == 0) {
          *(undefined4 *)((int)param_1 + 0xc) = *(undefined4 *)(iVar5 + 0x74);
        }
        else {
          *(undefined4 *)(*(int *)(iVar5 + 0x78) + 0x74) = *(undefined4 *)(iVar5 + 0x74);
        }
        *(int *)((int)param_1 + 8) = *(int *)((int)param_1 + 8) + -1;
        *(undefined4 *)(iVar5 + 0x74) = *(undefined4 *)((int)param_1 + 0x34);
        *(undefined4 *)(iVar5 + 0x78) = 0;
        if (*(int *)((int)param_1 + 0x34) != 0) {
          *(int *)(*(int *)((int)param_1 + 0x34) + 0x78) = iVar5;
        }
        *(int *)((int)param_1 + 0x34) = iVar5;
        iVar5 = iVar2;
      }
      *(undefined4 *)((int)param_1 + 0xc) = 0;
      CSoundManager__StopAllActiveVoices(&DAT_00896988);
      puVar3 = *(undefined4 **)param_1;
      while (puVar4 = puVar3, puVar4 != (undefined4 *)0x0) {
        puVar3 = (undefined4 *)puVar4[0x1d];
        if (puVar4 != (undefined4 *)0x0) {
          (**(code **)*puVar4)(1);
        }
      }
      *(undefined4 *)param_1 = 0;
      MEM_MANAGER__Cleanup();
      CSoundManager__LoadCompressedSampleBank(&DAT_00896988,'\0');
    }
  }
  return;
}
