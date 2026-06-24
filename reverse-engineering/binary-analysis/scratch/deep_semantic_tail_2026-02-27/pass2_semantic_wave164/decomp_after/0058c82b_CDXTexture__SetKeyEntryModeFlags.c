/* address: 0x0058c82b */
/* name: CDXTexture__SetKeyEntryModeFlags */
/* signature: void __thiscall CDXTexture__SetKeyEntryModeFlags(void * this, void * param_1, int param_2, uint param_3) */


void __thiscall CDXTexture__SetKeyEntryModeFlags(void *this,void *param_1,int param_2,uint param_3)

{
  int iVar1;
  uint *puVar2;
  void *unaff_ESI;

  iVar1 = CDXTexture__InsertOrFindKeyInSortedTable(this,(int)param_1,(uint)&param_1,unaff_ESI);
  if (-1 < iVar1) {
    if (param_2 == 0xff) {
      puVar2 = (uint *)(*(int *)((int)this + 0x1c) + (int)param_1 * 4);
      *puVar2 = *puVar2 & 0x20;
      puVar2 = (uint *)((int)param_1 * 4 + *(int *)((int)this + 0x1c));
      *puVar2 = *puVar2 | 1;
    }
    else if (param_2 == 0x10) {
      puVar2 = (uint *)(*(int *)((int)this + 0x1c) + (int)param_1 * 4);
      *puVar2 = *puVar2 | 0x10;
    }
    else {
      puVar2 = (uint *)(*(int *)((int)this + 0x1c) + (int)param_1 * 4);
      *puVar2 = *puVar2 & 0xfffffff0;
      puVar2 = (uint *)((int)param_1 * 4 + *(int *)((int)this + 0x1c));
      *puVar2 = *puVar2 | param_2 & 0xfU;
    }
  }
  return;
}
