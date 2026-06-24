/* address: 0x005115b0 */
/* name: CWorldPhysicsManager__Unk_005115b0 */
/* signature: int __cdecl CWorldPhysicsManager__Unk_005115b0(void * param_1) */


int __cdecl CWorldPhysicsManager__Unk_005115b0(void *param_1)

{
  int iVar1;

  iVar1 = stricmp(param_1,&DAT_00633b64);
  if (iVar1 == 0) {
    return 1;
  }
  iVar1 = stricmp(param_1,&DAT_00633b5c);
  if (iVar1 == 0) {
    return 2;
  }
  iVar1 = stricmp(param_1,&DAT_00633b54);
  if (iVar1 == 0) {
    return 3;
  }
  iVar1 = stricmp(param_1,&DAT_00633b4c);
  if (iVar1 == 0) {
    return 4;
  }
  iVar1 = stricmp(param_1,&DAT_00633b44);
  if (iVar1 == 0) {
    return 5;
  }
  iVar1 = stricmp(param_1,&DAT_00633b3c);
  if (iVar1 == 0) {
    return 6;
  }
  iVar1 = stricmp(param_1,&DAT_00633b34);
  if (iVar1 == 0) {
    return 7;
  }
  iVar1 = stricmp(param_1,&DAT_00633b2c);
  if (iVar1 == 0) {
    return 8;
  }
  iVar1 = stricmp(param_1,&DAT_00633b24);
  if (iVar1 == 0) {
    return 9;
  }
  iVar1 = stricmp(param_1,s_SpawnerA_00633c64);
  if (iVar1 == 0) {
    return 10;
  }
  iVar1 = stricmp(param_1,s_SpawnerB_00633c58);
  if (iVar1 == 0) {
    return 0xb;
  }
  iVar1 = stricmp(param_1,s_SpawnerC_00633c4c);
  if (iVar1 == 0) {
    return 0xc;
  }
  iVar1 = stricmp(param_1,s_SpawnerD_00633c40);
  if (iVar1 == 0) {
    return 0xd;
  }
  iVar1 = stricmp(param_1,s_SpawnerE_00633c34);
  return (-(uint)(iVar1 != 0) & 0xfffffff2) + 0xe;
}
