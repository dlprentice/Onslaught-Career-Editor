/* address: 0x00449dc0 */
/* name: CWorld__LoadNamedMeshCacheFromBuffer */
/* signature: void __fastcall CWorld__LoadNamedMeshCacheFromBuffer(int param_1) */


void __fastcall CWorld__LoadNamedMeshCacheFromBuffer(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  int local_10c;
  int local_108;
  uint local_104;
  char local_100 [256];

  *(undefined4 *)(param_1 + 0x42c) = 0;
  CConsole__Status(&DAT_00663498,s_Loading_named_meshes_00628cbc);
  DXMemBuffer__ReadBytes(&local_108,4);
  local_10c = 0;
  if (0 < local_108) {
    do {
      DXMemBuffer__ReadBytes(&local_104,1);
      DXMemBuffer__ReadBytes(local_100,local_104 & 0xff);
      iVar4 = 0;
      local_100[local_104 & 0xff] = '\0';
      iVar3 = DAT_0089cdcc;
      if (0 < DAT_0089cdcc) {
        piVar5 = &DAT_0089c9cc;
        do {
          if ((*piVar5 != 0) &&
             (iVar1 = stricmp(local_100,(char *)(*piVar5 + 0x24)), iVar3 = DAT_0089cdcc, iVar1 == 0)
             ) goto LAB_00449eae;
          iVar4 = iVar4 + 1;
          piVar5 = piVar5 + 1;
        } while (iVar4 < iVar3);
      }
      if (iVar3 != 0xff) {
        uVar2 = CMesh__FindOrCreate(local_100,1);
        (&DAT_0089c9cc)[DAT_0089cdcc] = uVar2;
        if ((&DAT_0089c9cc)[DAT_0089cdcc] != 0) {
          DAT_0089cdcc = DAT_0089cdcc + 1;
        }
      }
LAB_00449eae:
      local_10c = local_10c + 1;
    } while (local_10c < local_108);
  }
  CConsole__StatusDone(&DAT_00663498,s_Loading_named_meshes_00628cbc,'\x01');
  return;
}
