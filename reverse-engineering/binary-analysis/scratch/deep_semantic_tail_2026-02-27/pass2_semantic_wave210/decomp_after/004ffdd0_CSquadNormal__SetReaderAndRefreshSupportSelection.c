/* address: 0x004ffdd0 */
/* name: CSquadNormal__SetReaderAndRefreshSupportSelection */
/* signature: void __thiscall CSquadNormal__SetReaderAndRefreshSupportSelection(void * this, int param_1, void * param_2, int param_3) */


void __thiscall
CSquadNormal__SetReaderAndRefreshSupportSelection(void *this,int param_1,void *param_2,int param_3)

{
  int unaff_EDI;

  CGenericActiveReader__SetReader((void *)((int)this + 0xc),(void *)param_1);
  CSquadNormal__SelectBestSupportOrEscort(*(void **)((int)this + 8),(void *)param_1,unaff_EDI);
  *(void **)((int)this + 0x10) = param_2;
  return;
}
