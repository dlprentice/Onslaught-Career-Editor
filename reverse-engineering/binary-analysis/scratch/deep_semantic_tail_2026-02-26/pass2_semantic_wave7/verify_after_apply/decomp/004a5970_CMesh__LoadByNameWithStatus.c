/* address: 0x004a5970 */
/* name: CMesh__LoadByNameWithStatus */
/* signature: int __thiscall CMesh__LoadByNameWithStatus(void * this, int param_1, void * param_2, int param_3) */


int __thiscall CMesh__LoadByNameWithStatus(void *this,int param_1,void *param_2,int param_3)

{
  int iVar1;
  char cVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  char *pcVar6;
  undefined4 *puVar7;
  char *pcVar8;
  char *pcVar9;
  char local_440 [4];
  char local_43c [4];
  char local_438 [4];
  char local_434;
  undefined4 local_433;
  undefined1 local_340 [308];
  char local_20c [256];
  char local_10c [256];
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d372b;
  local_c = ExceptionList;
  iVar5 = 0;
  ExceptionList = &local_c;
  sprintf(local_10c,s_Warning___Loading_mesh__s_manual_0062fafc);
  DebugTrace(local_10c);
  sprintf(local_20c,s_Loading_mesh__s_0062faec);
  CConsole__Status(&DAT_00663498,local_20c);
  cVar2 = *(char *)param_1;
  if (cVar2 != '\0') {
    iVar1 = param_1;
    do {
      if (cVar2 == '\\') {
        iVar5 = (1 - param_1) + iVar1;
      }
      cVar2 = *(char *)(iVar1 + 1);
      iVar1 = iVar1 + 1;
    } while (cVar2 != '\0');
  }
  local_440[0] = s_data_Meshes__0062fadc[0];
  local_440[1] = s_data_Meshes__0062fadc[1];
  local_440[2] = s_data_Meshes__0062fadc[2];
  local_440[3] = s_data_Meshes__0062fadc[3];
  local_438[0] = s_data_Meshes__0062fadc[8];
  local_438[1] = s_data_Meshes__0062fadc[9];
  local_438[2] = s_data_Meshes__0062fadc[10];
  local_438[3] = s_data_Meshes__0062fadc[0xb];
  local_434 = s_data_Meshes__0062fadc[0xc];
  local_43c[0] = s_data_Meshes__0062fadc[4];
  local_43c[1] = s_data_Meshes__0062fadc[5];
  local_43c[2] = s_data_Meshes__0062fadc[6];
  local_43c[3] = s_data_Meshes__0062fadc[7];
  puVar7 = &local_433;
  for (iVar1 = 0x3c; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar7 = 0;
    puVar7 = puVar7 + 1;
  }
  *(undefined2 *)puVar7 = 0;
  *(undefined1 *)((int)puVar7 + 2) = 0;
  uVar3 = 0xffffffff;
  pcVar6 = (char *)(iVar5 + param_1);
  do {
    pcVar9 = pcVar6;
    if (uVar3 == 0) break;
    uVar3 = uVar3 - 1;
    pcVar9 = pcVar6 + 1;
    cVar2 = *pcVar6;
    pcVar6 = pcVar9;
  } while (cVar2 != '\0');
  uVar3 = ~uVar3;
  iVar1 = -1;
  pcVar6 = local_440;
  do {
    pcVar8 = pcVar6;
    if (iVar1 == 0) break;
    iVar1 = iVar1 + -1;
    pcVar8 = pcVar6 + 1;
    cVar2 = *pcVar6;
    pcVar6 = pcVar8;
  } while (cVar2 != '\0');
  pcVar6 = pcVar9 + -uVar3;
  pcVar9 = pcVar8 + -1;
  for (uVar4 = uVar3 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
    *(undefined4 *)pcVar9 = *(undefined4 *)pcVar6;
    pcVar6 = pcVar6 + 4;
    pcVar9 = pcVar9 + 4;
  }
  for (uVar3 = uVar3 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
    *pcVar9 = *pcVar6;
    pcVar6 = pcVar6 + 1;
    pcVar9 = pcVar9 + 1;
  }
  uVar3 = 0xffffffff;
  pcVar6 = (char *)(iVar5 + param_1);
  do {
    pcVar9 = pcVar6;
    if (uVar3 == 0) break;
    uVar3 = uVar3 - 1;
    pcVar9 = pcVar6 + 1;
    cVar2 = *pcVar6;
    pcVar6 = pcVar9;
  } while (cVar2 != '\0');
  uVar3 = ~uVar3;
  pcVar6 = pcVar9 + -uVar3;
  pcVar9 = (char *)((int)this + 0x24);
  for (uVar4 = uVar3 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
    *(undefined4 *)pcVar9 = *(undefined4 *)pcVar6;
    pcVar6 = pcVar6 + 4;
    pcVar9 = pcVar9 + 4;
  }
  for (uVar3 = uVar3 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
    *pcVar9 = *pcVar6;
    pcVar6 = pcVar6 + 1;
    pcVar9 = pcVar9 + 1;
  }
  CChunker__CChunker();
  local_4 = 0;
  iVar5 = DXMemBuffer__OpenRead(local_440,0x11,1,0);
  if (iVar5 == 0) {
    CConsole__StatusDone(&DAT_00663498,local_20c,'\0');
    DXMemBuffer__Close();
    local_4 = 0xffffffff;
    CChunker__Destructor();
    iVar5 = 0;
  }
  else {
    iVar5 = CMesh__Load(local_340,param_2);
    DXMemBuffer__Close();
    CConsole__StatusDone(&DAT_00663498,local_20c,'\x01');
    local_4 = 0xffffffff;
    CChunker__Destructor();
  }
  ExceptionList = local_c;
  return iVar5;
}
