/* address: 0x00490f50 */
/* name: CWorld__CanLoadMapSection */
/* signature: int __thiscall CWorld__CanLoadMapSection(void * this, int param_1, int param_2, int param_3, int param_4) */


int __thiscall CWorld__CanLoadMapSection(void *this,int param_1,int param_2,int param_3,int param_4)

{
  char cVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  char *pcVar5;
  char *pcVar6;
  char *pcVar7;
  char local_40 [64];

  sprintf(local_40,s_Loading_map__d_0062da5c);
  if (param_3 == 0) {
    pcVar5 = s__geometry_only__0062da2c;
    if (param_2 == 0) {
      pcVar5 = s__nothing____0062da1c;
    }
  }
  else if (param_2 == 0) {
    pcVar5 = s__properties_only__0062da40;
  }
  else {
    pcVar5 = &DAT_0062da54;
  }
  uVar2 = 0xffffffff;
  do {
    pcVar7 = pcVar5;
    if (uVar2 == 0) break;
    uVar2 = uVar2 - 1;
    pcVar7 = pcVar5 + 1;
    cVar1 = *pcVar5;
    pcVar5 = pcVar7;
  } while (cVar1 != '\0');
  uVar2 = ~uVar2;
  iVar3 = -1;
  pcVar5 = local_40;
  do {
    pcVar6 = pcVar5;
    if (iVar3 == 0) break;
    iVar3 = iVar3 + -1;
    pcVar6 = pcVar5 + 1;
    cVar1 = *pcVar5;
    pcVar5 = pcVar6;
  } while (cVar1 != '\0');
  pcVar5 = pcVar7 + -uVar2;
  pcVar7 = pcVar6 + -1;
  for (uVar4 = uVar2 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
    *(undefined4 *)pcVar7 = *(undefined4 *)pcVar5;
    pcVar5 = pcVar5 + 4;
    pcVar7 = pcVar7 + 4;
  }
  for (uVar2 = uVar2 & 3; uVar2 != 0; uVar2 = uVar2 - 1) {
    *pcVar7 = *pcVar5;
    pcVar5 = pcVar5 + 1;
    pcVar7 = pcVar7 + 1;
  }
  DebugTrace(local_40);
  if (param_1 == -1) {
    return 1;
  }
  if (param_2 == 0) {
    if ((param_3 != 0) && (*(int *)((int)this + 0x93e4) != 0)) {
      DebugTrace(s_Map_properties_are_already_loade_0062d9c0);
      return 1;
    }
  }
  else if (*(int *)((int)this + 0x93e0) != 0) {
    DebugTrace(s_Map_geometry_is_already_loaded___0062d9f0);
    return 1;
  }
  return 0;
}
