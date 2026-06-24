/* address: 0x004a5500 */
/* name: CMesh__Unk_004a5500 */
/* signature: void __stdcall CMesh__Unk_004a5500(void * param_1, int param_2) */


void CMesh__Unk_004a5500(void *param_1,int param_2)

{
  int iVar1;

  iVar1 = stricmp(param_1,&DAT_0062fa94);
  if (iVar1 == 0) {
    *(undefined4 *)(param_2 + 0x10) = 0;
    return;
  }
  iVar1 = stricmp(param_1,&DAT_0062fa8c);
  if (iVar1 == 0) {
    *(undefined4 *)(param_2 + 0x10) = 1;
    return;
  }
  iVar1 = stricmp(param_1,&DAT_0062fa88);
  if (iVar1 == 0) {
    *(undefined4 *)(param_2 + 0x10) = 2;
    return;
  }
  iVar1 = stricmp(param_1,s_STAND_0062fa80);
  if (iVar1 == 0) {
    *(undefined4 *)(param_2 + 0x10) = 3;
    return;
  }
  iVar1 = stricmp(param_1,s_SHOOT_0062fa78);
  if (iVar1 == 0) {
    *(undefined4 *)(param_2 + 0x10) = 4;
    return;
  }
  iVar1 = stricmp(param_1,s_SHOOT1_0062fa70);
  if (iVar1 == 0) {
    *(undefined4 *)(param_2 + 0x10) = 5;
    return;
  }
  iVar1 = stricmp(param_1,s_SHOOT2_0062fa68);
  if (iVar1 == 0) {
    *(undefined4 *)(param_2 + 0x10) = 6;
    return;
  }
  iVar1 = stricmp(param_1,&DAT_0062fa64);
  if (iVar1 == 0) {
    *(undefined4 *)(param_2 + 0x10) = 8;
    return;
  }
  iVar1 = stricmp(param_1,s_HOVER_0062fa5c);
  if (iVar1 == 0) {
    *(undefined4 *)(param_2 + 0x10) = 9;
    return;
  }
  iVar1 = stricmp(param_1,s_SHOOTWALK_0062fa50);
  if (iVar1 == 0) {
    *(undefined4 *)(param_2 + 0x10) = 7;
    return;
  }
  iVar1 = stricmp(param_1,&DAT_0062fa48);
  if (iVar1 == 0) {
    *(undefined4 *)(param_2 + 0x10) = 10;
  }
  return;
}
