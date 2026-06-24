/* address: 0x0058a58d */
/* name: CTexture__Helper_0058a58d */
/* signature: int __stdcall CTexture__Helper_0058a58d(void * param_1) */


int CTexture__Helper_0058a58d(void *param_1)

{
  int *piVar1;
  byte bVar2;
  void *this;
  int iVar3;
  byte *pbVar4;
  int extraout_ECX;
  int unaff_EDI;
  byte *pbVar5;
  bool bVar6;

  iVar3 = CTexture__Helper_0058a578(*(void **)param_1);
  piVar1 = (int *)(extraout_ECX + 0x4c + iVar3 * 4);
  iVar3 = *piVar1;
  do {
    if (iVar3 == 0) {
LAB_0058a5f9:
      *(int *)((int)param_1 + 0xc) = *piVar1;
      *piVar1 = (int)param_1;
      return 0;
    }
    pbVar4 = *(byte **)*piVar1;
    pbVar5 = *(byte **)param_1;
    do {
      bVar2 = *pbVar5;
      bVar6 = bVar2 < *pbVar4;
      if (bVar2 != *pbVar4) {
LAB_0058a5d0:
        iVar3 = (1 - (uint)bVar6) - (uint)(bVar6 != 0);
        goto LAB_0058a5d5;
      }
      if (bVar2 == 0) break;
      bVar2 = pbVar5[1];
      bVar6 = bVar2 < pbVar4[1];
      if (bVar2 != pbVar4[1]) goto LAB_0058a5d0;
      pbVar5 = pbVar5 + 2;
      pbVar4 = pbVar4 + 2;
    } while (bVar2 != 0);
    iVar3 = 0;
LAB_0058a5d5:
    if (iVar3 < 0) goto LAB_0058a5f9;
    if (iVar3 == 0) {
      this = (void *)*piVar1;
      *piVar1 = *(int *)((int)this + 0xc);
      *(undefined4 *)((int)this + 0xc) = 0;
      CTexture__IncludeNodeDtor(this,(void *)0x1,unaff_EDI);
      goto LAB_0058a5f9;
    }
    piVar1 = (undefined4 *)*piVar1 + 3;
    iVar3 = *piVar1;
  } while( true );
}
