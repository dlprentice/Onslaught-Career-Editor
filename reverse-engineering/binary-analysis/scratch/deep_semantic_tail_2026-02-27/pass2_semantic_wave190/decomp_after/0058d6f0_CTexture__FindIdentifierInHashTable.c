/* address: 0x0058d6f0 */
/* name: CTexture__FindIdentifierInHashTable */
/* signature: int __thiscall CTexture__FindIdentifierInHashTable(void * this, int param_1, int param_2) */


int __thiscall CTexture__FindIdentifierInHashTable(void *this,int param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  undefined4 *puVar3;

  uVar1 = CTexture__HashIdentifierMod7((void *)param_1);
  puVar3 = *(undefined4 **)((int)this + uVar1 * 4);
  while( true ) {
    if (puVar3 == (undefined4 *)0x0) {
      return 0;
    }
    iVar2 = lstrcmpiA((LPCSTR)*puVar3,(LPCSTR)param_1);
    if (iVar2 == 0) break;
    puVar3 = (undefined4 *)puVar3[8];
  }
  return (int)puVar3;
}
