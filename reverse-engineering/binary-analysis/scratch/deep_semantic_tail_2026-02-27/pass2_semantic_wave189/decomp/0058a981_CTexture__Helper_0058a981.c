/* address: 0x0058a981 */
/* name: CTexture__Helper_0058a981 */
/* signature: int __stdcall CTexture__Helper_0058a981(void * param_1) */


int CTexture__Helper_0058a981(void *param_1)

{
  int *piVar1;
  byte bVar2;
  void *this;
  int iVar3;
  int extraout_ECX;
  byte *pbVar4;
  int unaff_EDI;
  byte *pbVar5;
  bool bVar6;

  iVar3 = CTexture__Helper_0058a578(param_1);
  piVar1 = (int *)(extraout_ECX + 0x4c + iVar3 * 4);
  iVar3 = *piVar1;
  do {
    if (iVar3 == 0) {
      return 0;
    }
    pbVar4 = *(byte **)*piVar1;
    pbVar5 = param_1;
    do {
      bVar2 = *pbVar5;
      bVar6 = bVar2 < *pbVar4;
      if (bVar2 != *pbVar4) {
LAB_0058a9c0:
        iVar3 = (1 - (uint)bVar6) - (uint)(bVar6 != 0);
        goto LAB_0058a9c5;
      }
      if (bVar2 == 0) break;
      bVar2 = pbVar5[1];
      bVar6 = bVar2 < pbVar4[1];
      if (bVar2 != pbVar4[1]) goto LAB_0058a9c0;
      pbVar5 = pbVar5 + 2;
      pbVar4 = pbVar4 + 2;
    } while (bVar2 != 0);
    iVar3 = 0;
LAB_0058a9c5:
    if (iVar3 < 0) {
      return 0;
    }
    if (iVar3 == 0) {
      this = (void *)*piVar1;
      *piVar1 = *(int *)((int)this + 0xc);
      *(undefined4 *)((int)this + 0xc) = 0;
      CTexture__IncludeNodeDtor(this,(void *)0x1,unaff_EDI);
      return 0;
    }
    piVar1 = (undefined4 *)*piVar1 + 3;
    iVar3 = *piVar1;
  } while( true );
}
