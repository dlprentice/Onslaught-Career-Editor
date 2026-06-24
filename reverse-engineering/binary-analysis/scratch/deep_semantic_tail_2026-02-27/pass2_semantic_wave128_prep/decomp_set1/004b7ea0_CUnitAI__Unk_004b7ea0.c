/* address: 0x004b7ea0 */
/* name: CUnitAI__Unk_004b7ea0 */
/* signature: void __fastcall CUnitAI__Unk_004b7ea0(void * param_1) */


void __fastcall CUnitAI__Unk_004b7ea0(void *param_1)

{
  char cVar1;
  int iVar2;
  void *to_read;
  char *pcVar3;
  uint uVar4;
  uint uVar5;
  char *pcVar6;
  float local_108;
  char local_104 [260];

  iVar2 = *(int *)((int)param_1 + 8);
  if ((*(int *)(iVar2 + 0x38) != 0) &&
     ((*(int *)(iVar2 + 0x30) == 0 || ((*(byte *)(*(int *)(iVar2 + 0x30) + 0x2c) & 4) != 0)))) {
    *(undefined4 *)((int)param_1 + 0x20) = 0x3f800000;
    *(undefined4 *)((int)param_1 + 0x24) = 1;
    local_108 = 0.5;
    CEventManager__AddEvent_TimeFromNow
              (&EVENT_MANAGER,&local_108,0xbba,param_1,0,(void *)0x0,(void *)0x0);
    return;
  }
  pcVar3 = CText__GetAudioNameById(&g_Text,*(int *)(iVar2 + 0x10));
  if (pcVar3 == (char *)0x0) {
    FromWCHAR(*(short **)(*(int *)((int)param_1 + 8) + 0xc));
    CConsole__Printf(&DAT_0066f580,s_ERROR__MB__No_sample_for_message_00630894);
    *(undefined4 *)(*(int *)((int)param_1 + 8) + 8) = 1;
  }
  else {
    CText__GetLanguageName(&g_Text);
    sprintf((char *)((int)param_1 + 0x1c0),s__s_messagebox__s_006308c4);
    to_read = *(void **)((int)param_1 + 8);
    if (DAT_0089698c != '\0') {
      sprintf(local_104,s_data_sounds__s_ogg_00630880);
      uVar4 = 0xffffffff;
      pcVar3 = (char *)((int)param_1 + 0x1c0);
      do {
        pcVar6 = pcVar3;
        if (uVar4 == 0) break;
        uVar4 = uVar4 - 1;
        pcVar6 = pcVar3 + 1;
        cVar1 = *pcVar3;
        pcVar3 = pcVar6;
      } while (cVar1 != '\0');
      uVar4 = ~uVar4;
      pcVar3 = pcVar6 + -uVar4;
      pcVar6 = (char *)&DAT_00704e74;
      for (uVar5 = uVar4 >> 2; uVar5 != 0; uVar5 = uVar5 - 1) {
        *(undefined4 *)pcVar6 = *(undefined4 *)pcVar3;
        pcVar3 = pcVar3 + 4;
        pcVar6 = pcVar6 + 4;
      }
      for (uVar4 = uVar4 & 3; uVar4 != 0; uVar4 = uVar4 - 1) {
        *pcVar6 = *pcVar3;
        pcVar3 = pcVar3 + 1;
        pcVar6 = pcVar6 + 1;
      }
      CGenericActiveReader__SetReader(&DAT_00704e70,to_read);
      CBinkOpenThread__WaitForThread();
      uVar4 = 0xffffffff;
      pcVar3 = local_104;
      do {
        pcVar6 = pcVar3;
        if (uVar4 == 0) break;
        uVar4 = uVar4 - 1;
        pcVar6 = pcVar3 + 1;
        cVar1 = *pcVar3;
        pcVar3 = pcVar6;
      } while (cVar1 != '\0');
      uVar4 = ~uVar4;
      pcVar3 = pcVar6 + -uVar4;
      pcVar6 = (char *)&DAT_00807288;
      for (uVar5 = uVar4 >> 2; uVar5 != 0; uVar5 = uVar5 - 1) {
        *(undefined4 *)pcVar6 = *(undefined4 *)pcVar3;
        pcVar3 = pcVar3 + 4;
        pcVar6 = pcVar6 + 4;
      }
      for (uVar4 = uVar4 & 3; uVar4 != 0; uVar4 = uVar4 - 1) {
        *pcVar6 = *pcVar3;
        pcVar3 = pcVar3 + 1;
        pcVar6 = pcVar6 + 1;
      }
      DAT_0080738c = 0;
      CBinkOpenThread__StartAsync();
      CUnitAI__Unk_004b8020(param_1);
      return;
    }
  }
  CUnitAI__Unk_004b8020(param_1);
  return;
}
