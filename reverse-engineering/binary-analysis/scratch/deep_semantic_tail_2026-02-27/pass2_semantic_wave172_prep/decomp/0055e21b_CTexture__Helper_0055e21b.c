/* address: 0x0055e21b */
/* name: CTexture__Helper_0055e21b */
/* signature: int __cdecl CTexture__Helper_0055e21b(void * param_1) */


int __cdecl CTexture__Helper_0055e21b(void *param_1)

{
  uint uVar1;
  uint uVar2;
  undefined *in_ECX;
  int iVar3;
  uint uVar4;
  uint unaff_EDI;
  byte *pbVar5;
  undefined *puVar6;

  while( true ) {
    if (DAT_00653a9c < 2) {
      uVar1 = (byte)PTR_DAT_00653890[(uint)*(byte *)param_1 * 2] & 8;
      in_ECX = PTR_DAT_00653890;
    }
    else {
      puVar6 = (undefined *)0x8;
      uVar1 = CTexture__Helper_00563951(in_ECX,(uint)*(byte *)param_1,8,unaff_EDI);
      in_ECX = puVar6;
    }
    if (uVar1 == 0) break;
    param_1 = (void *)((int)param_1 + 1);
  }
  uVar1 = (uint)*(byte *)param_1;
  pbVar5 = (byte *)((int)param_1 + 1);
  if ((uVar1 == 0x2d) || (uVar4 = uVar1, uVar1 == 0x2b)) {
    uVar4 = (uint)*pbVar5;
    pbVar5 = (byte *)((int)param_1 + 2);
  }
  iVar3 = 0;
  while( true ) {
    if (DAT_00653a9c < 2) {
      uVar2 = (byte)PTR_DAT_00653890[uVar4 * 2] & 4;
    }
    else {
      puVar6 = (undefined *)0x4;
      uVar2 = CTexture__Helper_00563951(in_ECX,uVar4,4,unaff_EDI);
      in_ECX = puVar6;
    }
    if (uVar2 == 0) break;
    iVar3 = (uVar4 - 0x30) + iVar3 * 10;
    uVar4 = (uint)*pbVar5;
    pbVar5 = pbVar5 + 1;
  }
  if (uVar1 == 0x2d) {
    iVar3 = -iVar3;
  }
  return iVar3;
}
