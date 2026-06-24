/* address: 0x004e2bb0 */
/* name: CUnit__BuildVoiceXapPathIfChanged */
/* signature: int __thiscall CUnit__BuildVoiceXapPathIfChanged(void * this, int param_1, void * param_2) */


int __thiscall CUnit__BuildVoiceXapPathIfChanged(void *this,int param_1,void *param_2)

{
  char cVar1;
  uint in_EAX;
  uint uVar2;
  uint uVar3;
  char *pcVar4;
  char *pcVar5;
  char local_c8 [200];

  if (*(char *)((int)this + 4) == '\0') {
    return in_EAX & 0xffffff00;
  }
  CText__GetLanguageName(&g_Text);
  sprintf(local_c8,PTR_s__s_data_sounds_sounds__s_pc_xap_0063e2a8);
  uVar2 = stricmp(local_c8,(char *)((int)this + 0x88));
  if (uVar2 == 0) {
    return 0;
  }
  if (param_1 != 0) {
    uVar2 = 0xffffffff;
    pcVar4 = local_c8;
    do {
      pcVar5 = pcVar4;
      if (uVar2 == 0) break;
      uVar2 = uVar2 - 1;
      pcVar5 = pcVar4 + 1;
      cVar1 = *pcVar4;
      pcVar4 = pcVar5;
    } while (cVar1 != '\0');
    uVar2 = ~uVar2;
    pcVar4 = pcVar5 + -uVar2;
    for (uVar3 = uVar2 >> 2; uVar3 != 0; uVar3 = uVar3 - 1) {
      *(undefined4 *)param_1 = *(undefined4 *)pcVar4;
      pcVar4 = pcVar4 + 4;
      param_1 = (int)(param_1 + 4);
    }
    for (uVar3 = uVar2 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
      *(char *)param_1 = *pcVar4;
      pcVar4 = pcVar4 + 1;
      param_1 = (int)(param_1 + 1);
    }
  }
  return CONCAT31((int3)(uVar2 >> 8),1);
}
