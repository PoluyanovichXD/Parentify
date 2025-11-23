class CurrentUrl{
    constructor(url){
      this.url = new URL(url);
      this.pathList = []
      this.url.pathname.split('/').forEach(item => {
        if(item!=''){
          this.pathList.push(item)
        }
      });
    }
    hasGet(){
      return this.url.searchParams.size>0;
    }
    getString(){
      return this.url.search;
    }
    get(key){
      if(this.url.searchParams.get(key)){
        return this.url.searchParams.get(key);
      } else{
        return null
      }
    }
    set(key,val){
      this.url.searchParams.set(key,val)
      return this
    }
    getList(key){
      if(this.url.searchParams.get(key)){
        return this.url.searchParams.getAll(key);
      } else{
        return []
      }
    }
  }
  var currentUrl = new CurrentUrl(window.location.href);
  $(document).ready(function() {
    var footer = document.getElementById('footer')
    if(footer){
      if(!footer.closest('.wrapper')){
        document.querySelector('.wrapper').append(footer)
      }
    }
    $('.opening_image,.aipsin_html_content>figure>img, .aipsin_html_content img').click(function(e) {
      ToggleModal(e)
    });
  });
  if(Array.prototype.equals)
      console.warn("Overriding existing Array.prototype.equals. Possible causes: New API defines the method, there's a framework conflict or you've got double inclusions in your code.");
  Array.prototype.equals = function (array) {
      if (!array)
          return false;
      if(array === this)
          return true;
      if (this.length != array.length)
          return false;
      for (var i = 0, l=this.length; i < l; i++) {
          if (this[i] instanceof Array && array[i] instanceof Array) {
              if (!this[i].equals(array[i]))
                  return false;       
          }           
          else if (this[i] != array[i]) { 
              return false;   
          }           
      }       
      return true;
  }
  Array.prototype.unique = function(){
    var array  = this
    function onlyUnique(value, index, array) {
      return array.indexOf(value) === index;
    }
    return array.filter(onlyUnique);
  }
  Array.prototype.groupByCount = function (array, key) {
    if(array.length==0){
      return {}
    } else if(isDict(!array[0])){
      return {}
    }
      return array.reduce((acc, obj) => {
        const property = obj[key];
        if(acc[property]){
            acc[property] += 1
        } else{
            acc[property] = 1
        }
        return acc;
    }, {});
  }
  Array.prototype.hasDuplicates = function(){
    var array  = this
    var valuesSoFar = Object.create(null);
      for (var i = 0; i < array.length; ++i) {
          var value = array[i];
          if (value in valuesSoFar) {
              return true;
          }
          valuesSoFar[value] = true;
      }
      return false;
  }
  Object.defineProperty(Array.prototype, "equals", {enumerable: false});
  
  Date.prototype.createDateAsUTC = function() {
    var date = this;
    return new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate(), date.getHours(), date.getMinutes(), date.getSeconds()));
  }
  Object.defineProperty(Date.prototype, "equals", {enumerable: false});
  
  var get_csrftoken = function(name) {
    var value = '; ' + document.cookie,
        parts = value.split('; ' + name + '=')
    if (parts.length == 2) return parts.pop().split(';').shift()
  }
  function uuidv4() {
    return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
      (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
  }
  function getRandom(min, max) {
    let difference = max - min;
    let rand = Math.random();
    rand = Math.floor( rand * difference);
    rand = rand + min;
    return rand;
  }
  function getRandomFloat(min, max, decimals=2) {
    const str = (Math.random() * (max - min) + min).toFixed(decimals);
    return parseFloat(str);
  }
  function getRandomBool(chance=0.5){
    return Math.random() < chance
  }
  async function PostFormData(url=null,data=null,redirect=false){
    var formData = new FormData()
    if(isDict(data)){
      for (const [key, value] of Object.entries(data)) {
        formData.set(key, value)
      }
    } else{
      formData = data;
    }
    return await PostData(url,formData,redirect)
  }
  async function PostData(url=null,data=null,redirect=false){
    var headers = {
      "X-Requested-With": "XMLHttpRequest",
      'X-CSRFToken':get_csrftoken('csrftoken')
    }
    if(data instanceof FormData){
      data = data
    }
    else if(typeof data == 'string' || typeof data == 'number'){
      data = data
    }else{
      data = JSON.stringify(data?data:{})
      headers['Accept'] = 'application/json';
      headers['Content-Type'] = 'application/json';
    }
    const data_post = await fetch(`${url?url:window.location.href}`,{
      method:'POST',
      headers:headers,
      body:data
      }).then(async (res)=>{
          if (res.ok){
            if(redirect){
              window.location.href = url?url:window.location.href
            }
            return res.json()
          } else{
            try {
              var error_json = await res.json()
              if(error_json.message){
                TOAST.AddToast({text:String(error_json.message),type:`error`})
                TOAST.ShowToasts()
              }
            } catch (error) {
              
            }
            return new Error(`${res.status} ${res.statusText}`)
          }
      }).catch((err)=>{
          return err
      })
      if(data_post instanceof Error){
        throw data_post
      }
      return data_post
  }
  async function GetData(url=null,redirect=false){
    const data_post = await fetch(`${url?url:window.location.href}`,{
      method:'GET',
      mode:'cors',
      headers:{
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          "X-Requested-With": "XMLHttpRequest",
          'X-CSRFToken':get_csrftoken('csrftoken'),
      }
      }).then(async (res)=>{
          if (res.ok){
            if(redirect){
              window.location.href = url?url:window.location.href
            }
            return res.json()
          } else{
            try {
              var error_json = await res.json()
              if(error_json.message){
                TOAST.AddToast({text:String(error_json.message),type:`error`})
                TOAST.ShowToasts()
              }
            } catch (error) {
              console.log(error)
            }
            return new Error(`Error: ${res.status} ${res.statusText}`)
          }
      }).catch((err)=>{
          return err
      })
      if(data_post instanceof Error){
        throw data_post
      }
      return data_post
  }
  async function PostFile(url=null,data=null,redirect=false){
    var headers = {
      "X-Requested-With": "XMLHttpRequest",
      'X-CSRFToken':get_csrftoken('csrftoken')
    }
    if(data instanceof FormData){
      data = data
    }
    else if(typeof data == 'string' || typeof data == 'number'){
      data = data
    }else{
      data = JSON.stringify(data?data:{})
      headers['Accept'] = 'application/json';
      headers['Content-Type'] = 'application/json';
    }
    const data_post = await fetch(`${url?url:window.location.href}`,{
      method:'POST',
      headers:headers,
      body:data
      }).then(async (res)=>{
          if (res.ok){
            if(redirect){
              window.location.href = url?url:window.location.href
            }
            return res.blob()
          } else{
            try {
              var error_json = await res.json()
              if(error_json.message){
                TOAST.AddToast({text:String(error_json.message),type:`error`})
                TOAST.ShowToasts()
              }
            } catch (error) {
              
            }
            return new Error(`${res.status} ${res.statusText}`)
          }
      }).catch((err)=>{
          return err
      })
      if(data_post instanceof Error){
        throw data_post
      }
      return data_post
  }
  async function GetFile(url=null,redirect=false){
    const data_post = await fetch(`${url?url:window.location.href}`,{
      method:'GET',
      headers:{
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          "X-Requested-With": "XMLHttpRequest",
          'X-CSRFToken':get_csrftoken('csrftoken')
      }
      }).then(async (res)=>{
          if (res.ok){
            if(redirect){
              window.location.href = url?url:window.location.href
            }
            return res.blob()
          } else{
            try {
              var error_json = await res.json()
              if(error_json.message){
                TOAST.AddToast({text:String(error_json.message),type:`error`})
                TOAST.ShowToasts()
              }
            } catch (error) {
              
            }
            return new Error(`Error: ${res.status} ${res.statusText}`)
          }
      }).catch((err)=>{
          return err
      })
      if(data_post instanceof Error){
        throw data_post
      }
      return data_post
  }
  class DictUtils {
    static entries(dictionary) {
        try {
            return Object.entries(dictionary);
        } catch (error) {
            return Object.keys(dictionary).map(function(key) {
                return [key, dictionary[key]];
            });
        }
    }
    static sort(dictionary, sort='asc') {
      return DictUtils.entries(dictionary)
          .sort((kv0,kv1)=>{
            if(sort=='desc'){
              return kv1[1] - kv0[1];
            } else if(sort=='asc'){
              return kv0[1] - kv1[1];
            }
            return kv0;
          })
          .reduce((sorted, kv)=>{
              sorted[kv[0]] = kv[1]; 
              return sorted;
          }, {});
    }
    static isEmpty(dictionary) {
      if(!DictUtils.isDict(dictionary)){
        return null
      }
      for (const prop in dictionary) {
        if (Object.hasOwn(dictionary, prop)) {
          return false;
        }
      }
      return true;
    }
    static isDict(d) {
      return !!d && typeof d==='object' && d!==null && !(d instanceof Array) && !(d instanceof Date) && isJsonable(d);
    }
  }