/* address: 0x0044a1f0 */
/* name: CResourceAccumulator__LoadAndCopyMixerTextureSet */
/* signature: void __thiscall CResourceAccumulator__LoadAndCopyMixerTextureSet(void * this, int param_1, int param_2) */


void __thiscall CResourceAccumulator__LoadAndCopyMixerTextureSet(void *this,int param_1,int param_2)

{
  CMapTex__LoadMixerTextureSet(param_1,6,0x100);
  CMapTex__CopyFromOther(*(undefined4 *)((int)this + 0x49c));
  CMapTex__CopyFromOther(*(int *)((int)this + 0x49c) + 0x4c);
  CMapTex__CopyFromOther(*(int *)((int)this + 0x49c) + 0x98);
  CMapTex__CopyFromOther(*(int *)((int)this + 0x49c) + 0xe4);
  CMapTex__CopyFromOther(*(int *)((int)this + 0x49c) + 0x130);
  CMapTex__CopyFromOther(*(int *)((int)this + 0x49c) + 0x17c);
  return;
}
